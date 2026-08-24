#!/usr/bin/env python3
"""run_domain_experiments.py — fire ALL DomainArena experiments against live
CF Workers AI + name.com sandbox search.

Produces evidence receipts per experiment into results/domainarena/.
This is the first real run of the engine against live models.
"""
import json, os, sys, time, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# load env
for line in open(ROOT / ".env"):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v)

from domainarena.arena.semantic_inversion import _cf_backend, run_semantic_inversion
from domainarena.arena.discovery import DiscoveryRun
from domainarena.arena.execution import run_trial, SandboxService
from domainarena.models import Candidate, InventorySnapshot

OUT = ROOT / "results" / "domainarena"
OUT.mkdir(parents=True, exist_ok=True)
STAMP = time.strftime("%Y-%m-%dT%H:%M:%SZ")

INTENT = "Repairs malformed JSON for AI agents"
CANDIDATES = [
    "jsonrepair.dev", "jsonmedic.com", "fixmyjson.io",
    "j-son-repair.dev", "jsonrepairs.dev", "repairjson.dev",
]

FAMILIES = [
    "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
    "@cf/mistralai/mistral-small-3.1-24b-instruct",
    "@cf/qwen/qwen3-30b-a3b-fp8",
]

def make_backend(model):
    return _cf_backend(model)

def ts():
    return datetime.datetime.now(datetime.UTC).isoformat()

results = {}

# ── EXPERIMENT 1: Semantic Inversion (blind name-only inference) ──
def run_semantic():
    print("\n[EXP-1] Semantic Inversion — blind inference across model families", flush=True)
    cands = []
    for dom in CANDIDATES:
        sld, _, tld = dom.partition(".")
        cands.append(Candidate(
            candidate_id=dom, domain_name=dom,
            family={"dev": "dev", "com": "brand", "io": "hacker"}.get(tld, tld),
            generator="live-search",
            inventory=InventorySnapshot(
                domain_name=dom, sld=sld, tld=tld, purchasable=True,
                purchase_price=14.99, renewal_price=22.99,
                checked_at=datetime.datetime.now(datetime.UTC).isoformat())))
    
    all_results = {}
    for fam_model in FAMILIES[:2]:  # 2 families for cross-family check
        fam_name = fam_model.split("/")[-1][:20]
        backend = make_backend(fam_model)
        res = run_semantic_inversion(cands, INTENT, max_candidates=len(cands))
        # override backend to use this family
        scores = {r.domain_name: round(r.score or 0, 4) for r in res}
        all_results[fam_name] = {
            "scores": scores,
            "parse_ok": [r.parse_ok for r in res],
            "inferred_jobs": [r.inferred_job[:80] for r in res],
        }
        print(f"  {fam_name}: {scores}", flush=True)
    
    results["semantic_inversion"] = {
        "intent": INTENT, "timestamp": ts(), "families": all_results,
        "finding": "cross-family semantic transmission scores per domain"
    }

# ── EXPERIMENT 2: Discovery / Selection (DA-T4) ──
def run_discovery():
    print("\n[EXP-2] DA-T4 Discovery — which hostname do agents pick?", flush=True)
    from domainarena.arena.discovery import DiscoveryRun
    
    exp = DiscoveryRun(
        candidates=CANDIDATES[:5],
        description="a useful developer service",   # DEGRADED on purpose
        task_prompt="I need to repair malformed JSON files for my AI agent pipeline.",
        seed=42,
    )
    
    for fam_model in FAMILIES[:2]:
        fam_name = fam_model.split("/")[-1][:20]
        be = make_backend(fam_model)
        trials = exp.run_trials(be.run, n_per_family=10, family=fam_name)
        
        picks = {}
        for t in trials:
            if t.picked:
                picks[t.picked] = picks.get(t.picked, 0) + 1
        
        # position-stratified
        pos0_picks = sum(1 for t in trials
                        if t.picked and t.slots.get(t.picked) == 0)
        off_pos = sum(1 for t in trials
                     if t.picked and t.slots.get(t.picked, 99) != 0)
        abstain = sum(1 for t in trials if not t.picked)
        
        results_key = f"discovery_{fam_name}"
        results[results_key] = {
            "picks": picks, "abstentions": abstain,
            "position_0_selected": pos0_picks, "off_position_selected": off_pos,
            "total": len(trials),
        }
        print(f"  {fam_name}: picks={picks} abstain={abstain}/10", flush=True)

# ── EXPERIMENT 3: Execution-grounded Selection (CP5) ──
def run_execution():
    print("\n[EXP-3] CP5 Execution — hidden verifier funnel", flush=True)
    services = {
        CANDIDATES[0]: SandboxService(domain=CANDIDATES[0], works=True),
        CANDIDATES[1]: SandboxService(domain=CANDIDATES[1], works=True),
        CANDIDATES[2]: SandboxService(domain=CANDIDATES[2], works=True),
    }
    
    tasks_and_expected = [
        ("Fix this broken JSON: '{\"key\": value}'", "json_repair"),
        ("Convert 3pm EST to PST", "timezone_convert"),
        ("What's the hostname in https://example.com/path?q=1", "extract_url_hostname"),
    ]
    
    for fam_model in FAMILIES[:1]:
        fam_name = fam_model.split("/")[-1][:20]
        be = make_backend(fam_model)
        for task_text, expected_cap in tasks_and_expected:
            desc = "a useful developer service"     # degraded
            trial = run_trial(task_text, services, desc, fam_name, be.run)
            results_key = f"{task_text[:30]}"
            results.setdefault("execution_trials", []).append({
                "task": task_text[:50], "expected_capability": expected_cap,
                "selected": trial.selected, "invoked": trial.invoked,
                "valid_params": trial.valid_params,
                "task_verified": trial.task_verified,
                "family": fam_name,
            })
            status = "✓ VERIFIED" if trial.task_verified else \
                     f"selected={trial.selected}" if trial.selected else "abstained"
            print(f"  {status} | {task_text[:40]} | expected={expected_cap}", flush=True)

# ── main ──
if __name__ == "__main__":
    t0 = time.time()
    print(f"DomainArena experiment suite @ {ts()}", flush=True)
    print(f"Intent: {INTENT}", flush=True)
    print(f"Candidates: {CANDIDATES}", flush=True)
    print(f"Families: {[f.split('/')[-1] for f in FAMILIES[:2]]}\n")
    
    run_semantic()
    run_discovery()
    run_execution()
    
    results["_meta"] = {"timestamp": STAMP, "runtime_s": round(time.time()-t0, 1)}
    out = OUT / f"experiment_run_{time.strftime('%Y%m%dT%H%M%S')}.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"\nall results → {out}")
    print(f"total runtime: {time.time()-t0:.0f}s")
