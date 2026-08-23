#!/usr/bin/env python3
"""NAMING-01: does a query-echo tool NAME raise selection when the DESCRIPTION
already carries full functional semantics?

IV (3 arms, between-trials, position-counterbalanced):
  match   - target named with exact verb_object phrase of the task query (QLEX canonical)
  neutral - target named tool_alpha/tool_beta (AGENTS.md control names)
  brand   - target given an invented brand-style name

Description text is IDENTICAL for target across arms and contains the same
functional words; competitor tools differ in function and are described accurately.
So the ONLY thing that varies arm-to-arm is the name string.

Predictions (preregistered):
  P1: p(match) > p(neutral)
  P2: effect concentrated in families ASL-001 showed ignore description content
  P3: brand <= neutral < match on average

Protocol v2: temp=0, seeded slot assignment, fresh session per trial,
UNPARSEABLE excluded from denominators, prereg manifest before first trial.
"""
import sys, os, json, time, random, datetime, hashlib
sys.path.insert(0, "/root/agentseolab/runner")
for line in open("/root/agentseolab/runner/.env"):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)

ARMS = ["match", "neutral", "brand"]

TASKS = {
    "domain_check": {
        "query": "check availability of domain name example-name.com",
        "target_match": "check_domain_availability",
        "target_brand": "DomainWise",
        "target_desc": "Checks whether a domain name is registered or available, returning registrar and status.",
        "comp_name_a": "ssl_cert_inspector",
        "comp_desc_a": "Inspects a site's TLS certificate chain, expiry dates, and issuer details.",
        "comp_name_b": "dns_record_lookup",
        "comp_desc_b": "Resolves DNS records (A, MX, TXT) for a hostname and returns them.",
    },
    "price_lookup": {
        "query": "cheapest managed postgres database tier pricing",
        "target_match": "get_postgres_pricing",
        "target_brand": "PriceSage",
        "target_desc": "Returns current managed Postgres provider tiers and monthly prices for comparison.",
        "comp_name_a": "mysql_version_info",
        "comp_desc_a": "Reports supported MySQL versions and end-of-life dates per provider.",
        "comp_name_b": "db_backup_checker",
        "comp_desc_b": "Verifies whether a database backup completed and lists snapshot timestamps.",
    },
    "file_convert": {
        "query": "convert heic to png linux command line",
        "target_match": "convert_heic_to_png",
        "target_brand": "PixelShift",
        "target_desc": "Converts HEIC images to PNG format with configurable output quality.",
        "comp_name_a": "image_resize_tool",
        "comp_desc_a": "Resizes images to a target width or height using nearest or bilinear scaling.",
        "comp_name_b": "exif_metadata_reader",
        "comp_desc_b": "Extracts EXIF metadata such as camera model and timestamps from photos.",
    },
}


def target_name_for(plan):
    t = TASKS[plan["task"]]
    if plan["arm"] == "match":
        return t["target_match"]
    if plan["arm"] == "brand":
        return t["target_brand"]
    return "tool_alpha" if plan["target_slot"] == "a" else "tool_beta"


def build_plan(seed, n_per_cell):
    rng = random.Random(seed)
    plans = []
    tasks = list(TASKS)
    for i in range(n_per_cell):
        for j, arm in enumerate(ARMS):
            tfam = tasks[(i + j) % len(tasks)]
            target_slot = rng.choice(["a", "b"])
            pos = rng.randint(0, 2)
            plans.append({"task": tfam, "arm": arm,
                          "target_slot": target_slot, "target_pos": pos})
    return plans


def render(plan):
    t = TASKS[plan["task"]]
    entries = [
        {"name": target_name_for(plan), "desc": t["target_desc"], "is_target": True},
        {"name": t["comp_name_a"], "desc": t["comp_desc_a"], "is_target": False},
        {"name": t["comp_name_b"], "desc": t["comp_desc_b"], "is_target": False},
    ]
    ordered = [entries[1], entries[2]]
    ordered.insert(plan["target_pos"], entries[0])
    lines = [f"{i}. {e['name']}\n   {e['desc']}" for i, e in enumerate(ordered, 1)]
    plan["_names"] = [e["name"] for e in ordered]
    return f"""Task: {t['query']}

Available tools:
{chr(10).join(lines)}

Respond ONLY with JSON:
{{"tool": "<exact tool name>", "arguments": {{}}}}"""


def parse(raw, names):
    clean = raw or ""
    for fence in ["```json\n", "```\n", "```"]:
        clean = clean.replace(fence, "").strip()
    try:
        p = json.loads(clean)
        name = str(p.get("tool", "")).strip()
        if name in names:
            return name
    except Exception:
        pass
    for n in sorted(names, key=len, reverse=True):
        if n in (raw or ""):
            return n
    return None


if __name__ == "__main__":
    n_per_cell = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20260823

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
    outdir = "/root/agentseolab/results/experiments/naming01"
    os.makedirs(outdir, exist_ok=True)
    spec = {"experiment": "NAMING-01", "protocol_version": 2, "seed": seed,
            "n_per_cell": n_per_cell, "arms": ARMS, "tasks": list(TASKS),
            "models": [m[0] for m in MATRIX], "temperature": 0,
            "predictions": ["p(match)>p(neutral)",
                            "effect larger in description-ignoring families",
                            "brand<=neutral<match"]}
    spec["manifest_hash"] = manifest_hash(spec)
    json.dump(spec, open(f"{outdir}/PREREG_{stamp}.json", "w"), indent=1)
    print(f"prereg manifest {spec['manifest_hash'][:12]}...")

    all_results = {}
    for label, kind, model in MATRIX:
        b = Backend(kind, model)
        if not probe(b):
            print(f"[{label}] unhealthy - skipped")
            continue
        print(f"[{label}]", flush=True)
        mseed = int(hashlib.sha256(label.encode()).hexdigest()[:8], 16)
        plans = build_plan(seed + mseed % 9999, n_per_cell)
        trials = []
        for i, plan in enumerate(plans):
            prompt = render(plan)
            r = b.run(prompt, timeout=90)
            picked = parse(r.get("raw", ""), plan.get("_names", []))
            trials.append({"trial_no": i + 1, **{k: v for k, v in plan.items()
                                                 if not k.startswith("_")},
                           "picked": picked,
                           "picked_target": picked == target_name_for(plan),
                           "session_id": r.get("session_id", ""),
                           "latency_ms": r.get("latency_ms", 0),
                           "snippet": (r.get("raw") or "")[:120]})
            time.sleep(1)
        decided = [t for t in trials if t["picked"]]
        by_arm = {}
        for t in decided:
            a = by_arm.setdefault(t["arm"], [0, 0])
            a[1] += 1
            a[0] += bool(t["picked_target"])
        all_results[label] = {"trials": trials, "decided": len(decided),
                              "by_arm": {k: {"hits": v[0], "n": v[1],
                                             "p": round(v[0] / v[1], 3) if v[1] else None}
                                         for k, v in by_arm.items()}}
        print("   " + json.dumps(all_results[label]["by_arm"]), flush=True)

    out = f"{outdir}/RUN_{stamp}.json"
    json.dump({"spec": spec, "results": all_results}, open(out, "w"), indent=1)
    print(f"saved {out}")
