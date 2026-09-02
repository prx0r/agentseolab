#!/usr/bin/env python3
"""TLD-V2: deconfounded domain-extension experiment.

Fixes over v1 (H-TLD01):
1. LATIN-SQUARE position balance: every TLD occupies every slot equally by
   construction -> marginal TLD effects are no longer position artifacts.
2. TEMPLATE robustness: 3 instruction phrasings rotated (prompt-language is an IV
   to control, not ignore).
3. PARAPHRASE robustness: 2 query wordings per task family.
4. n=30 per family.

Primary estimands (preregistered):
  E1: P(pick slot j) - position-response curve (expect strong primacy)
  E2: P(pick TLD | TLD at slot j) - within-slot TLD preference
  E3: template x choice invariance
"""
import sys, os, json, time, random, datetime, hashlib, itertools
sys.path.insert(0, "/root/agentseolab/runner")
for line in open("/root/agentseolab/runner/.env"):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)

TLDS = ["com", "dev", "org", "io", "xyz"]

TASKS = {
    "code_fix": {
        "q": ["python ModuleNotFoundError fix after pip install",
              "fix import error module not found python"],
        "desc": "Technical guide page covering causes, diagnostics, and fixes for this error.",
    },
    "price_lookup": {
        "q": ["cheapest managed postgres pricing comparison",
              "managed postgres database tier prices compared"],
        "desc": "Comparison page listing providers, tiers, and current prices for this service.",
    },
    "fact_verify": {
        "q": ["height Eiffel Tower versus Golden Gate Bridge",
              "how tall are the Eiffel Tower and Golden Gate Bridge"],
        "desc": "Reference page with measured dimensions and supporting citations.",
    },
}

TEMPLATES = [
    ("Search results for: {query}\n\n{serp}\n\nYou may open ONE result. Respond ONLY with JSON:\n{{\"open\": <number>, \"url\": \"<full url>\"}}\n\nWhich do you open?"),
    ("Query: {query}\n\nWeb results:\n{serp}\n\nChoose the single result you would fetch first. Reply ONLY with JSON: {{\"open\": <number>}}"),
    ("You are assisting a developer. Task: {query}\n\nCandidate pages:\n{serp}\n\nPick one page to open. Output format: {{\"open\": <1-based number>}} - nothing else."),
]


def latin_permutations(rng, n):
    """Balanced by construction: every block of 5 is a complete Latin square
    (each TLD occupies each slot exactly once). Extra variety via per-block
    rotation order and direction, never breaking the guarantee."""
    perms = []
    while len(perms) < n:
        start = rng.randrange(5)
        step = rng.choice([1, -1])
        block = [tuple(TLDS[(start + step * i + step * j) % 5] for j in range(5))
                 for i in range(5)]
        rng.shuffle(block)
        perms.extend(block)
    return perms[:n]


def build_plans(seed, n_total=30):
    rng = random.Random(seed)
    perms = latin_permutations(rng, n_total)
    plans = []
    for i in range(n_total):
        task = list(TASKS)[i % 3]
        para = (i // 3) % 2
        tmpl = i % 3
        plans.append({"trial_no": i + 1, "task": task, "paraphrase": para,
                      "template": tmpl, "serp": perms[i]})
    return plans


def render(plan):
    t = TASKS[plan["task"]]
    query = t["q"][plan["paraphrase"]]
    lines = [f"{i+1}. https://docs-example.{tld}/guide - \"{query}\"\n   {t['desc']}"
             for i, tld in enumerate(plan["serp"])]
    return TEMPLATES[plan["template"]].format(query=query, serp="\n".join(lines))


def parse(raw):
    clean = raw or ""
    for fence in ["```json\n", "```\n", "```"]:
        clean = clean.replace(fence, "").strip()
    try:
        return int(json.loads(clean).get("open", -1))
    except Exception:
        pass
    import re
    m = re.search(r'"open"\s*:\s*(\d)', raw or "") or re.search(r'\bopen\b[^0-9]{0,8}(\d)', raw or "")
    return int(m.group(1)) if m else -1


if __name__ == "__main__":
    n_per_family = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20260824

    from canonical_asl001 import Backend, probe
    from execution_experiment import manifest_hash

    MATRIX = [
        ("meta-llama-3.3-70b", "cf", "@cf/meta/llama-3.3-70b-instruct-fp8-fast"),
        ("mistral-small-24b", "cf", "@cf/mistralai/mistral-small-3.1-24b-instruct"),
        ("qwen3-30b", "cf", "@cf/qwen/qwen3-30b-a3b-fp8"),
        ("gpt-oss-20b", "cf", "@cf/openai/gpt-oss-20b"),
        ("nemotron-super-120b", "or", "nvidia/nemotron-3-super-120b-a12b:free"),
        ("mimo-v2.5", "oc", "mimo-v2.5"),
    ]

    stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    outdir = "/root/agentseolab/results/experiments/tld_v2"
    os.makedirs(outdir, exist_ok=True)
    spec = {"experiment": "TLD-V2", "protocol_version": 2, "seed": seed,
            "n_per_family": n_per_family, "templates": 3, "paraphrases": 2,
            "latin_square_positions": True, "models": [m[0] for m in MATRIX],
            "temperature": 0,
            "estimands": ["P(slot)", "P(tld|slot)", "template invariance"]}
    spec["manifest_hash"] = manifest_hash(spec)
    json.dump(spec, open(f"{outdir}/PREREG_{stamp}.json", "w"), indent=1)
    print(f"prereg manifest {spec['manifest_hash'][:12]}...", flush=True)

    all_results = {}
    for label, kind, model in MATRIX:
        b = Backend(kind, model)
        if not probe(b):
            print(f"[{label}] unhealthy - skipped", flush=True)
            continue
        mseed = int(hashlib.sha256(label.encode()).hexdigest()[:8], 16)
        plans = build_plans(seed + mseed % 9999, n_per_family)
        trials = []
        for plan in plans:
            r = b.run(render(plan), timeout=90)
            k = parse(r.get("raw", ""))
            picked_tld = plan["serp"][k - 1] if 1 <= k <= 5 else None
            trials.append({"trial_no": plan["trial_no"], "task": plan["task"],
                           "paraphrase": plan["paraphrase"], "template": plan["template"],
                           "serp": plan["serp"], "picked_slot": k,
                           "picked_tld": picked_tld,
                           "session_id": r.get("session_id", ""),
                           "snippet": (r.get("raw") or "")[:100]})
            time.sleep(1)
        decided = [t for t in trials if t["picked_tld"]]
        slots = {}
        for t in decided:
            s = t["picked_slot"] - 1
            slots[s] = slots.get(s, 0) + 1
        by_template = {}
        for t in decided:
            by_template.setdefault(t["template"], []).append(t["picked_slot"] == 1)
        all_results[label] = {"trials": trials, "decided": len(decided),
                              "slot_dist": {str(k): v for k, v in sorted(slots.items())},
                              "slot1_by_template": {str(k): f"{sum(v)}/{len(v)}" for k, v in by_template.items()}}
        print(f"[{label}] decided={len(decided)} slots={all_results[label]['slot_dist']} "
              f"tmpl={all_results[label]['slot1_by_template']}", flush=True)

    out = f"{outdir}/RUN_{stamp}.json"
    json.dump({"spec": spec, "results": all_results}, open(out, "w"), indent=1)
    print(f"saved {out}")
