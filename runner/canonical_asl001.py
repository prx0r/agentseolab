#!/usr/bin/env python3
"""Canonical ASL-001 v2 batch: runs the protocol-compliant experiment across the
canonical model matrix with per-provider adapters (temp=0, UA headers, usage logging).

Usage: python3 runner/canonical_asl001.py [n_per_model] [seed]
"""
import sys, os, json, time, datetime, hashlib
sys.path.insert(0, "/root/agentseolab/runner")
sys.path.insert(0, "/root/agentseolab/providers")

for line in open("/root/agentseolab/runner/.env"):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)

from execution_experiment import build_trial_plan, run_trial, manifest_hash, PROTOCOL_VERSION
from track_usage import log_call
import urllib.request

N = int(sys.argv[1]) if len(sys.argv) > 1 else 30
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 20260823

# Canonical matrix M1-M9 (docs/experiments-rules.md §1). Provider = adapter below.
MATRIX = [
    ("M1", "meta-llama-3.3-70b",   "cf", "@cf/meta/llama-3.3-70b-instruct-fp8-fast"),
    ("M2", "mistral-small-24b",    "cf", "@cf/mistralai/mistral-small-3.1-24b-instruct"),
    ("M3", "qwen3-30b",            "cf", "@cf/qwen/qwen3-30b-a3b-fp8"),
    ("M5", "gpt-oss-20b",          "cf", "@cf/openai/gpt-oss-20b"),
    ("M6", "gemma-4-26b",          "cf", "@cf/google/gemma-4-26b-a4b-it"),  # OpenRouter 429; CF is live equivalent
    ("M8", "nemotron-super-120b",  "or", "nvidia/nemotron-3-super-120b-a12b:free"),
    ("M9", "ox-alpha-free",        "oc", "ox-alpha-free"),
]

ENDPOINTS = {
    "cf": ("https://api.cloudflare.com/client/v4/accounts/" + os.environ.get("CF_ACCOUNT_ID", "") + "/ai/run/",
           os.environ.get("CF_TOKEN")),
    "hf": ("https://router.huggingface.co/v1/chat/completions", os.environ.get("HF_TOKEN")),
    "or": ("https://openrouter.ai/api/v1/chat/completions", os.environ.get("OPENROUTER_API_KEY")),
    "oc": ("https://opencode.ai/zen/go/v1/chat/completions", os.environ.get("OPENCODE_GO_API_KEY")),
}


def call(kind, model, prompt, timeout=120):
    t0 = time.time()
    if kind == "cf":
        url = ENDPOINTS["cf"][0] + model
    else:
        url = ENDPOINTS[kind][0]
    key = ENDPOINTS[kind][1]
    body_obj = {"messages": [{"role": "user", "content": prompt}], "max_tokens": 1200, "temperature": 0}
    if kind != "cf":
        body_obj["model"] = model  # CF: model in URL only; mistral-small 404s if duplicated in body
    body = json.dumps(body_obj).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Authorization": f"Bearer {key}", "Content-Type": "application/json",
        "User-Agent": "agentseolab/2.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read())
            hdrs = r.headers
        res = d.get("result", {})
        if "choices" in res:
            msg = res["choices"][0].get("message", {})
        elif "choices" in d:
            msg = d["choices"][0].get("message", {})
        else:
            msg = {}
        text = (msg.get("content") or res.get("response") or "").strip()
        log_call(kind, model, int((time.time() - t0) * 1000), bool(text), hdrs if kind != "cf" else None)
        return {"ok": bool(text), "raw": text,
                "latency_ms": int((time.time() - t0) * 1000),
                "session_id": f"{kind}_{time.time_ns()}"}
    except Exception as e:
        log_call(kind, model, int((time.time() - t0) * 1000), False, None)
        return {"ok": False, "raw": "", "error": str(e)[:100],
                "session_id": f"{kind}_{time.time_ns()}", "latency_ms": int((time.time() - t0) * 1000)}


class Backend:
    def __init__(self, kind, model):
        self.kind, self.model = kind, model
        self.name = kind
    def run(self, prompt, timeout=120):
        return call(self.kind, self.model, prompt, timeout)


def probe(b, attempts=3):
    for a in range(attempts):
        r = b.run("Reply with exactly: OK", timeout=60)
        if r.get("ok") and bool((r.get("raw") or "").strip()):
            return True
        time.sleep(5)  # transient CF cold-start 404s / slow reasoning models
    return False


if __name__ == "__main__":
    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    outdir = "/root/agentseolab/results/experiments/asl001_v2"
    os.makedirs(outdir, exist_ok=True)

    spec = {
        "experiment": "ASL-001", "protocol_version": PROTOCOL_VERSION,
        "hypothesis_id": "H-ASL001a",
        "hypothesis": "Agents select tools by description quality independent of execution capability",
        "treatment": "plain_working executes; control compelling_broken always fails",
        "metric": "picked_working among decided selections (Wilson CI); secondary TASK_VERIFIED",
        "seed": SEED, "n_per_model": N, "temperature": 0,
        "matrix": [{"id": m[0], "label": m[1], "provider": m[2], "model": m[3]} for m in MATRIX],
        "rules_doc": "docs/experiments-rules.md",
    }
    spec["manifest_hash"] = manifest_hash(spec)
    pre = f"{outdir}/PREREG_{stamp}.json"
    json.dump(spec, open(pre, "w"), indent=1)
    print(f"preregistered {pre}\n  manifest {spec['manifest_hash'][:16]}…\n")

    all_results = {}
    for mid, label, kind, model in MATRIX:
        b = Backend(kind, model)
        if not probe(b):
            print(f"[{mid}] {label}: UNHEALTHY — skipped, recorded")
            all_results[label] = {"status": "unhealthy"}
            continue
        print(f"[{mid}] {label} ({model})")
        plans = build_trial_plan(SEED + hash(mid) % 10000, N)
        trials = []
        for i, plan in enumerate(plans):
            r = run_trial(b, plan, i + 1)
            trials.append(r)
            sel = "OK" if r.get("picked_working") else "WRONG"
            print(f"   t{i+1}: tool={str(r.get('selected_tool', '?'))[:16]:16s} pick={sel}")
            time.sleep(1.5)  # pace free tiers
        decided = [t for t in trials if t.get("executed")]
        wins = sum(1 for t in decided if t.get("picked_working"))
        succ = sum(1 for t in trials if t.get("task_succeeded"))
        all_results[label] = {"status": "ok", "decided": len(decided), "wins": wins,
                              "task_success": succ, "trials": trials}
        print(f"   => {wins}/{len(decided)} picked working · task success {succ}/{N}\n")

    out = f"{outdir}/RUN_{stamp}.json"
    json.dump({"spec": spec, "results": all_results}, open(out, "w"), indent=1)
    print(f"saved: {out}")

    # quick summary table
    sys.path.insert(0, "/root/agentseolab/analysis")
    from wilson import wilson
    print(f"\n{'model':22s} {'wins/decided':>12s} {'p':>6s} {'CI95':>18s} sig")
    for label, res in all_results.items():
        if res.get("status") != "ok" or not res["decided"]:
            print(f"{label:22s} {'—':>12s}")
            continue
        w = wilson(res["wins"], res["decided"])
        print(f"{label:22s} {str(res['wins'])+'/'+str(res['decided']):>12s} "
              f"{w['p']:>6} {str(w['ci95']):>18s} {'*' if w['excludes_0.5'] else ''}")
