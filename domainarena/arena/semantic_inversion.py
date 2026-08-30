"""Semantic Inversion MVP — cheap proxy stage, never ground truth.

Given a hostname alone (blind: no intent shown), an evaluator infers what the
product does; we score overlap against the frozen intent's concepts.
Evaluator families rotate per AGENTS.md model policy.
"""
from __future__ import annotations
import json
import os
import re
import sys
from dataclasses import dataclass, field

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))

from domainarena.models import Candidate  # noqa: E402

PROMPT = """You are shown ONLY a domain name. Infer what product or service it belongs to.

Domain: {domain}

Reply with JSON only:
{{"inferred_job": "<one sentence>", "audience": "consumer|business|developer|ai_agent", "concepts": ["<word>", ...]}}
"""

FAMILIES = [
    "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    "@cf/mistralai/mistral-small-3.1-24b-instruct",
    "@cf/qwen/qwen3-30b-a3b-fp8",
]


@dataclass
class InversionResult:
    candidate_id: str
    domain_name: str
    family: str
    inferred_job: str
    audience_guess: str | None
    concepts: list[str] = field(default_factory=list)
    score: float | None = None  # semantic transmission score [0,1]
    parse_ok: bool = True


def _tokenize(text: str) -> set[str]:
    stop = {"the", "a", "an", "for", "and", "with", "of", "to", "in", "on", "is", "it"}
    return {w for w in re.findall(r"[a-z][a-z0-9]+", text.lower()) if w not in stop}


def score_inference(intent_text: str, inferred_job: str,
                    concepts: list[str]) -> float:
    """Deterministic concept-overlap scoring between frozen intent and blind inference."""
    a = _tokenize(intent_text)
    b = _tokenize(inferred_job) | {c.lower() for c in concepts}
    if not a or not b:
        return 0.0
    return len(a & b) / len(a)


def _heuristic_family(domain: str, intent_text: str) -> InversionResult:
    """Offline deterministic evaluator used when no inference quota is available."""
    sld = domain.partition(".")[0]
    words = re.findall(r"[a-z]+", re.sub(r"([a-z])([A-Z])", r"\1 \2", sld.lower()))
    return InversionResult(
        candidate_id="offline", domain_name=domain, family="heuristic-offline",
        inferred_job=" ".join(words),
        audience_guess=None,
        concepts=words,
        score=score_inference(intent_text, " ".join(words), words),
        parse_ok=True,
    )


def _parse_llm_json(raw: str) -> dict | None:
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _cf_backend(model: str):
    """Minimal Cloudflare Workers AI adapter (free-tier rotation per AGENTS.md).

    Kept local so the product layer never depends on lab runner internals.
    """
    import time
    import urllib.request
    import uuid
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "") or os.environ.get("CF_ACCOUNT_ID", "")
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "") or os.environ.get("CF_TOKEN", "")

    class _B:
        name, model_id = "cloudflare-workers-ai", model

        def run(self, prompt: str, timeout: int = 60) -> dict:
            url = (f"https://api.cloudflare.com/client/v4/accounts/{account}"
                   f"/ai/run/{model}")
            body = json.dumps({"messages": [{"role": "user", "content": prompt}],
                               "max_tokens": 1200, "temperature": 0}).encode()
            req = urllib.request.Request(url, data=body, headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"})
            t0 = time.time()
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    res = json.loads(r.read()).get("result", {})
                latency_ms = int((time.time() - t0) * 1000)
                msg = (res.get("choices") or [{}])[0].get("message", {}) \
                    if "choices" in res else {}
                text = (msg.get("content") or res.get("response") or "").strip()
                return {"ok": bool(text), "raw": text,
                        "session_id": "cf_" + uuid.uuid4().hex[:10],
                        "latency_ms": latency_ms}
            except Exception as e:
                return {"ok": False, "raw": "", "error": str(e)[:120],
                        "session_id": "cf_" + uuid.uuid4().hex[:10],
                        "latency_ms": int((time.time() - t0) * 1000)}

    return _B()


def run_semantic_inversion(candidates: list[Candidate], intent_text: str,
                           families: list[str] | None = None,
                           max_candidates: int | None = None) -> list[InversionResult]:
    """Blind name-only inference across evaluator families.

    Uses the free Cloudflare Workers AI rotation when CF_TOKEN is present;
    otherwise falls back to the offline deterministic evaluator so the pipeline
    always produces evidence-shaped output.
    """
    fams = families or FAMILIES[:1]
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "") or os.environ.get("CF_TOKEN", "")
    results: list[InversionResult] = []
    use_live = bool(token and (os.environ.get("CLOUDFLARE_ACCOUNT_ID") or os.environ.get("CF_ACCOUNT_ID")))

    if use_live:
        try:
            probe = _cf_backend(fams[0])
            if not probe.run("Reply with the single word OK")["ok"]:
                use_live = False
        except Exception:
            use_live = False

    cands = candidates if max_candidates is None else candidates[:max_candidates]
    for cand in cands:
        if not use_live:
            results.append(_heuristic_family(cand.domain_name, intent_text))
            continue
        for fam in fams:
            be = _cf_backend(fam)
            resp = be.run(PROMPT.format(domain=cand.domain_name))
            if not resp.get("ok"):
                results.append(InversionResult(
                    candidate_id=cand.candidate_id,
                    domain_name=cand.domain_name, family=fam,
                    inferred_job="", audience_guess=None, score=0.0,
                    parse_ok=False))
                continue
            data = _parse_llm_json(resp["raw"]) or {}
            job = data.get("inferred_job", "")
            concepts = data.get("concepts", []) or []
            results.append(InversionResult(
                candidate_id=cand.candidate_id,
                domain_name=cand.domain_name, family=fam,
                inferred_job=str(job),
                audience_guess=data.get("audience"),
                concepts=[str(c) for c in concepts],
                score=score_inference(intent_text, str(job), [str(c) for c in concepts]),
                parse_ok=bool(data),
            ))
    return results


def aggregate(results: list[InversionResult]) -> dict[str, float]:
    """Per-candidate mean transmission score across families (parse failures count)."""
    agg: dict[str, list[float]] = {}
    for r in results:
        agg.setdefault(r.domain_name, []).append(r.score or 0.0)
    return {d: sum(v) / len(v) for d, v in agg.items()}
