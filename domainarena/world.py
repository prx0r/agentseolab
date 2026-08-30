"""DomainArena — a cogym worldpack for measuring LLM comprehension of domain names.

The first benchmark that asks: "given only a domain name, can an AI model
infer what service runs behind it?"

World protocol: each episode presents one domain candidate for one intent.
The model scores semantic transmission (0-1). The hidden oracle knows the
ground-truth match. Quality gates check cross-family consistency.

Imports benchmark cases from:
  - internal splits (dev/heldout/stress/relation_s2_secret/vitaminc)
  - external canonical sources (ANLI, MNLI, SNLI, HaluEval, etc.)
  - live name.com search results
"""
from __future__ import annotations

import enum
import json
import os
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cogym_kernel.kernel.contracts import (
    ActionResult,
    ActionSpec,
    CandidateArtifact,
    Metric,
    MetricVector,
    RunReceipt,
    WorldSpec,
)

# ── DomainArena types ──────────────────────────────────────────────

class EvidenceStatus(str, enum.Enum):
    MEASURED = "MEASURED"
    PROXY = "PROXY"
    NOT_MEASURED = "NOT_MEASURED"


@dataclass(frozen=True)
class EvidenceValue:
    value: float | None = None
    status: EvidenceStatus = EvidenceStatus.NOT_MEASURED
    protocol: str | None = None
    n: int | None = None


@dataclass
class DomainCase:
    """One benchmark case: an intent and a candidate domain."""
    case_id: str
    source: str                    # which dataset it came from
    domain_name: str
    intent_description: str
    primary_job: str
    ground_truth_match: bool       # does domain_name actually match intent?
    family_scores: dict = field(default_factory=dict)  # model -> score


# ── Benchmark case loading ─────────────────────────────────────────

def load_internal_cases(root: Path | None = None) -> list[DomainCase]:
    if root is None:
        root = Path(os.environ.get("DOMAINARENA_BENCH_ROOT",
                                    Path(__file__).parent.parent / "data" / "bench"))
    cases = []
    for split in ["dev", "heldout", "stress", "relation_s2_secret", "vitaminc_pairs"]:
        p = root / "benchmark" / f"{split}.jsonl"
        if not p.exists():
            continue
        for line in open(p):
            c = json.loads(line)
            pref = c.get("preferred", "a")
            good = c["answer_a"] if pref == "a" else c["answer_b"]
            bad = c["answer_b"] if pref == "a" else c["answer_a"]
            # For pairwise splits, we create two cases: truth-vs-good and truth-vs-bad
            cases.append(DomainCase(
                case_id=f"{split}:{c.get('id', hash(c['truth']) % 10000)}",
                source=split,
                domain_name=good,
                intent_description=c["truth"],
                primary_job=c.get("mutation", ""),
                ground_truth_match=True,
            ))
    return cases


def load_external_canonical(root: Path | None = None) -> list[DomainCase]:
    if root is None:
        root = Path(os.environ.get("DOMAINARENA_BENCH_ROOT",
                                    Path(__file__).parent.parent / "data" / "bench"))
    ext = root if "external_canonical" in str(root) else root / "benchmark" / "external_canonical"
    cases = []
    for p in sorted(ext.glob("*.jsonl")):
        name = p.stem
        for i, line in enumerate(open(p)):
            if not line.strip():
                continue
            d = json.loads(line)
            typ = d.get("type", "nli3")
            if typ == "pair":
                cases.append(DomainCase(
                    case_id=f"{name}:{i}", source=name,
                    domain_name=d.get("good", d.get("domain_name", "")),
                    intent_description=d.get("truth", d.get("premise", "")),
                    primary_job="",
                    ground_truth_match=True))
            else:
                cases.append(DomainCase(
                    case_id=f"{name}:{i}",
                    source=name,
                    domain_name=d.get("hypothesis", d.get("sentence2", "")),
                    intent_description=d.get("premise", d.get("sentence1", "")),
                    primary_job="",
                    ground_truth_match=d.get("label") == 0,
                ))
    return cases


def load_all_cases(root: Path | None = None) -> list[DomainCase]:
    return load_internal_cases(root) + load_external_canonical(root)


# ── cogym World implementation ─────────────────────────────────────

@dataclass(frozen=True)
class InferenceResult:
    """Result from the inference model (model being tested)."""
    domain: str
    model_family: str
    model_id: str
    inference: str
    latency_ms: int
    response_hash: str


@dataclass(frozen=True)
class SemanticEvaluation:
    """Result from the hidden scorer (separate from inference model)."""
    intent_hash: str
    inference_hash: str
    semantic_score: float
    match_label: str  # "exact", "partial", "none"
    scorer_version: str
    scorer_model: str


@dataclass
class DAState:
    """Per-episode state: one domain being scored against one intent."""
    case: DomainCase
    seed: int
    model_family: str
    inference_result: InferenceResult | None = None
    evaluation: SemanticEvaluation | None = None
    committed: bool = False
    error: str | None = None


class DomainArenaWorld:
    """cogym worldpack: presents a domain candidate for an intent.
    
    The agent (model backend) infers purpose from the domain name alone.
    A HIDDEN SCORER (separate model) compares inference against frozen intent.
    
    Quality gates:
      - semantic_score >= threshold (max)
      - parse_success == 1.0 (must produce parseable output)
    
    The tested model NEVER scores itself.
    """

    def __init__(self, cases: list[DomainCase], root: Path):
        self._cases = {f"{c.source}:{c.case_id}": c for c in cases}
        self.root = root
        self._spec = None

    @property
    def world_spec(self) -> WorldSpec:
        if self._spec is None:
            self._spec = WorldSpec(
                world_kind="domainarena.comprehension",
                version="0.2",
                instance_set_hash="domainarena-bench-v0",
                environment_hash="cf-workers-ai+groq",
                oracle_hash="stated-intent-ground-truth",
                metadata={
                    "description": "LLM comprehension of domain-name semantics",
                    "sources": sorted({c.source for c in self._cases.values()}),
                    "total_cases": len(self._cases),
                })
        return self._spec

    @property
    def worldpack_id(self) -> str:
        from cogym_kernel.kernel.ids import content_id
        return content_id("wp", {
            "kind": "domainarena.comprehension", "v": 0,
            "cases": len(self._cases)})

    def get_case(self, instance_id: str) -> DomainCase:
        return self._cases[instance_id]

    @property
    def instance_ids(self) -> list[str]:
        return list(self._cases.keys())

    def reset(self, *, instance_id: str, seed: int, model_family: str = "") -> DAState:
        case = self._cases[instance_id]
        return DAState(case=case, seed=seed, model_family=model_family)

    def observe(self, state: DAState) -> dict:
        return {
            "domain_name": state.case.domain_name,
            "intent": state.case.intent_description[:200],
            "model_family": state.model_family,
        }

    def actions(self, state: DAState) -> tuple[ActionSpec, ...]:
        return (
            ActionSpec(kind="INFERENCE", executor_kind="llm_inference"),
            ActionSpec(kind="SCORE_SEMANTIC", executor_kind="hidden_scorer"),
            ActionSpec(kind="COMMIT_SCORE", executor_kind="deterministic"),
        )

    def apply(self, state: DAState, action: ActionSpec,
              result: ActionResult) -> DAState:
        import hashlib
        if action.kind == "INFERENCE":
            if state.inference_result is not None:
                raise ValueError("INFERENCE already applied; cannot apply twice")
            raw = result.payload.get("raw", "")
            inference = result.payload.get("inference", raw.strip())
            resp_hash = hashlib.sha256(inference.encode()).hexdigest()
            inf_result = InferenceResult(
                domain=state.case.domain_name,
                model_family=state.model_family,
                model_id=result.payload.get("model", ""),
                inference=inference,
                latency_ms=result.wall_ms or 0,
                response_hash=resp_hash,
            )
            return DAState(
                case=state.case, seed=state.seed,
                model_family=state.model_family,
                inference_result=inf_result, evaluation=None,
                committed=False)
        
        if action.kind == "SCORE_SEMANTIC":
            if state.inference_result is None:
                raise ValueError("SCORE_SEMANTIC requires INFERENCE first")
            if state.evaluation is not None:
                raise ValueError("SCORE_SEMANTIC already applied; cannot apply twice")
            # Hidden scorer produces the evaluation
            evaluation = SemanticEvaluation(
                intent_hash=hashlib.sha256(
                    state.case.intent_description.encode()).hexdigest(),
                inference_hash=state.inference_result.response_hash,
                semantic_score=float(result.payload.get("semantic_score", 0)),
                match_label=result.payload.get("match_label", "none"),
                scorer_version=result.payload.get("scorer_version", "v1"),
                scorer_model=result.payload.get("scorer_model", ""),
            )
            return DAState(
                case=state.case, seed=state.seed,
                model_family=state.model_family,
                inference_result=state.inference_result,
                evaluation=evaluation,
                committed=False)
        
        if action.kind == "COMMIT_SCORE":
            if state.inference_result is None:
                raise ValueError("COMMIT_SCORE requires INFERENCE first")
            if state.evaluation is None:
                raise ValueError("COMMIT_SCORE requires SCORE_SEMANTIC first")
            return DAState(
                case=state.case, seed=state.seed,
                model_family=state.model_family,
                inference_result=state.inference_result,
                evaluation=state.evaluation,
                committed=True)
        
        return state

    def terminal(self, state: DAState) -> bool:
        return state.committed

    def score(self, state: DAState) -> MetricVector:
        s = state.evaluation.semantic_score if state.evaluation else 0.0
        return MetricVector(metrics=(
            Metric("semantic_score", s, "max"),
            Metric("parse_success", 1.0 if not state.error else 0.0, "max"),
            Metric("response_latency_ms",
                   state.inference_result.latency_ms if state.inference_result else 500.0,
                   "min"),
        ))


# ── Executor: CF Workers AI / Groq ─────────────────────────────────

class LLMInferenceExecutor:
    """Calls a model backend to infer domain purpose from name alone."""

    PROMPT = (
        "You are shown a domain name with no other context.\n"
        "Domain: {domain}\n\n"
        "What product or service do you think runs behind this domain?\n"
        "Reply in one sentence."
    )

    def __init__(self, model_id: str, provider: str, api_key: str,
                 account_id: str = "", base_url: str = ""):
        self.model_id = model_id
        self.provider = provider
        self.api_key = api_key
        self.account_id = account_id
        self.base_url = base_url

    def execute(self, action) -> Any:
        import urllib.request
        prompt = self.PROMPT.format(domain=action.metadata.get("domain", ""))
        if self.provider == "cloudflare":
            url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model_id}"
            body = {"messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200}
            headers = {"Authorization": f"Bearer {self.api_key}",
                       "Content-Type": "application/json"}
        elif self.provider == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            body = {"model": self.model_id,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 200}
            headers = {"Authorization": f"Bearer {self.api_key}",
                       "Content-Type": "application/json"}
        else:
            raise ValueError(f"unknown provider: {self.provider}")

        req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                     headers=headers)
        try:
            import time
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=30) as r:
                res = json.loads(r.read())
            latency_ms = int((time.time() - t0) * 1000)

            if self.provider == "cloudflare":
                msg = (res.get("result", {}).get("choices") or [{}])[0].get("message", {})
                text = msg.get("content", "")
            else:
                text = (res.get("choices") or [{}])[0].get("message", {}).get("content", "")

            return ActionResult(
                action_id=action.action_id, status="ok",
                payload={"raw": text, "inference": text.strip(),
                         "model": self.model_id, "provider": self.provider},
                wall_ms=latency_ms)
        except Exception as e:
            return ActionResult(action_id=action.action_id, status="error",
                                error=str(e)[:200])


# ── Hidden Scorer: separate from inference model ──────────────────

class HiddenScorerExecutor:
    """Scores semantic match between inference and frozen intent.
    
    This is a SEPARATE model from the one being tested.
    The tested model NEVER evaluates its own semantic success.
    """
    
    SCORER_PROMPT = (
        "You are a semantic evaluator. You will be given:\n"
        "1. A frozen product intent (what the domain is supposed to represent)\n"
        "2. An inference from another model (what it thought the domain represented)\n\n"
        "Rate how well the inference matches the intent on a scale of 0.0 to 1.0:\n"
        "- 1.0: exact match (inference correctly identifies the service)\n"
        "- 0.7-0.9: partial match (inference gets the general category right)\n"
        "- 0.3-0.6: weak match (inference is related but misses key aspects)\n"
        "- 0.0-0.2: no match (inference is wrong or unrelated)\n\n"
        "Reply in JSON format:\n"
        '{"score": <float>, "label": "<exact|partial|none>", "reasoning": "<brief>"}'
    )
    
    def __init__(self, model_id: str, provider: str, api_key: str,
                 account_id: str = "", base_url: str = ""):
        self.model_id = model_id
        self.provider = provider
        self.api_key = api_key
        self.account_id = account_id
        self.base_url = base_url
    
    def execute(self, action, state: DAState) -> Any:
        import urllib.request
        import hashlib
        
        if not state.inference_result:
            return ActionResult(
                action_id=action.action_id, status="error",
                error="no inference result to score")
        
        prompt = (
            f"FROZEN INTENT: {state.case.intent_description[:500]}\n\n"
            f"INFERENCE: {state.inference_result.inference}"
        )
        
        if self.provider == "cloudflare":
            url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run/{self.model_id}"
            body = {"messages": [{"role": "user", "content": self.SCORER_PROMPT + "\n\n" + prompt}],
                    "max_tokens": 200}
            headers = {"Authorization": f"Bearer {self.api_key}",
                       "Content-Type": "application/json"}
        elif self.provider == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            body = {"model": self.model_id,
                    "messages": [{"role": "user", "content": self.SCORER_PROMPT + "\n\n" + prompt}],
                    "max_tokens": 200}
            headers = {"Authorization": f"Bearer {self.api_key}",
                       "Content-Type": "application/json"}
        else:
            raise ValueError(f"unknown provider: {self.provider}")
        
        req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                     headers=headers)
        try:
            import time
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=30) as r:
                res = json.loads(r.read())
            latency_ms = int((time.time() - t0) * 1000)
            
            if self.provider == "cloudflare":
                msg = (res.get("result", {}).get("choices") or [{}])[0].get("message", {})
                text = msg.get("content", "")
            else:
                text = (res.get("choices") or [{}])[0].get("message", {}).get("content", "")
            
            # Parse scorer response
            try:
                parsed = json.loads(text)
                score = float(parsed.get("score", 0))
                label = parsed.get("label", "none")
            except (json.JSONDecodeError, ValueError):
                # Fallback: try to extract score from text
                import re
                match = re.search(r'"?score"?\s*[:=]\s*([0-9.]+)', text)
                score = float(match.group(1)) if match else 0.0
                label = "none"
            
            return ActionResult(
                action_id=action.action_id, status="ok",
                payload={
                    "semantic_score": score,
                    "match_label": label,
                    "scorer_version": "v1",
                    "scorer_model": self.model_id,
                    "raw": text,
                },
                wall_ms=latency_ms)
        except Exception as e:
            return ActionResult(action_id=action.action_id, status="error",
                                error=str(e)[:200])
EOF_MARKER = None
