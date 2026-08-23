#!/usr/bin/env python3
"""NAMING-02: factorial name-style x description-strength.

NAMING-01 found a ceiling null: informative descriptions exhaustively determine
choice, names have zero marginal effect. This experiment creates discriminability
headroom via DEGRADED descriptions (generic text that does not identify function)
and tests whether the NAME becomes the operative channel.

Design (2x3, preregistered):
  description: {informative, degraded} x name-style on target: {echo, neutral, brand}
  competitor: single plausible functional tool for a DIFFERENT function,
              fixed across arms (its name is informative in both blocks).

Primary estimand: name-style effect WITHIN degraded arm (interaction).
Predictions:
  P1: informative block replicates ceiling (p~1.0 all arms) [H-NAMING01]
  P2: degraded block shows echo > chance
  P3: ordering echo > brand > neutral within degraded
"""
import sys, os, json, time, random, datetime, hashlib
sys.path.insert(0, "/root/agentseolab/runner")
for line in open("/root/agentseolab/runner/.env"):
    if "=" in line and not line.startswith("#"):
        k, v = line.strip().split("=", 1)
        os.environ.setdefault(k, v)

ARMS = ["echo", "neutral", "brand"]
BLOCKS = ["informative", "degraded"]

TASKS = {
    "domain_check": {
        "query": "check availability of domain name example-name.com",
        "target_echo": "check_domain_availability",
        "target_brand": "DomainWise",
        "desc_full": "Checks whether a domain name is registered or available, returning registrar and status.",
        "comp_name": "ssl_cert_inspector",
    },
    "price_lookup": {
        "query": "cheapest managed postgres database tier pricing",
        "target_echo": "get_postgres_pricing",
        "target_brand": "PriceSage",
        "desc_full": "Returns current managed Postgres provider tiers and monthly prices for comparison.",
        "comp_name": "mysql_version_info",
    },
    "file_convert": {
        "query": "convert heic to png linux command line",
        "target_echo": "convert_heic_to_png",
        "target_brand": "PixelShift",
        "desc_full": "Converts HEIC images to PNG format with configurable output quality.",
        "comp_name": "image_resize_tool",
    },
}

DESC_DEGRADED = "General-purpose utility for common web and file tasks."
COMP_DEGRADED = "Helper tool for website and data operations."


def target_name_for(plan):
    t = TASKS[plan["task"]]
    if plan["arm"] == "echo":
        return t["target_echo"]
    if plan["arm"] == "brand":
        return t["target_brand"]
    return "tool_alpha" if plan["slot"] == "a" else "tool_beta"


def build_plans(seed, n_per_cell):
    rng = random.Random(seed)
    plans = []
    tasks = list(TASKS)
    for i in range(n_per_cell):
        for bi, block in enumerate(BLOCKS):
            for ai, arm in enumerate(ARMS):
                task = tasks[(i + ai + bi) % len(tasks)]
                slot = rng.choice(["a", "b"])
                pos = rng.randint(0, 1)
                plans.append({"trial_no": len(plans) + 1, "task": task,
                              "block": block, "arm": arm, "slot": slot, "pos": pos})
    return plans


def render(plan):
    t = TASKS[plan["task"]]
    tname = target_name_for(plan)
    tdesc = t["desc_full"] if plan["block"] == "informative" else DESC_DEGRADED
    cdesc = t["comp_desc"] if False else (
        ("Inspects a site's TLS certificate chain, expiry dates, and issuer details."
         if plan["task"] == "domain_check" else
         "Reports supported MySQL versions and end-of-life dates per provider."
         if plan["task"] == "price_lookup" else
         "Resizes images to a target width or height using nearest or bilinear scaling.")
        if plan["block"] == "informative" else COMP_DEGRADED)
    comp = t["comp_name"]
    entries = [
        {"name": tname, "desc": tdesc, "target": True},
        {"name": comp, "desc": cdesc, "target": False},
    ]
    ordered = entries[::-1] if plan["pos"] == 1 else entries
    plan["_names"] = [e["name"] for e in ordered]
    lines = [f"{i+1}. {e['name']}\n   {e['desc']}" for i, e in enumerate(ordered)]
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
    outdir = "/root/agentseolab/results/experiments/naming02"
    os.makedirs(outdir, exist_ok=True)
    spec = {"experiment": "NAMING-02", "protocol_version": 2, "seed": seed,
            "n_per_cell": n_per_cell, "arms": ARMS, "blocks": BLOCKS,
            "models": [m[0] for m in MATRIX], "temperature": 0,
            "predictions": ["informative replicates ceiling", "degraded: echo>chance",
                            "degraded ordering echo>brand>neutral"]}
    spec["manifest_hash"] = manifest_hash(spec)
    json.dump(spec, open(f"{outdir}/PREREG_{stamp}.json", "w"), indent=1)
    print(f"prereg manifest {spec['manifest_hash'][:12]}...", flush=True)

    all_results = {}
    for label, kind, model in MATRIX:
        b = Backend(kind, model)
        if not probe(b):
            print(f"[{label}] unhealthy - skipped", flush=True)
            continue
        print(f"[{label}]", flush=True)
        mseed = int(hashlib.sha256(label.encode()).hexdigest()[:8], 16)
        plans = build_plans(seed + mseed % 9999, n_per_cell)
        trials = []
        for plan in plans:
            prompt = render(plan)
            r = b.run(prompt, timeout=90)
            picked = parse(r.get("raw", ""), plan.get("_names", []))
            trials.append({**{k: v for k, v in plan.items() if not k.startswith("_")},
                           "picked": picked,
                           "picked_target": picked == target_name_for(plan),
                           "session_id": r.get("session_id", ""),
                           "snippet": (r.get("raw") or "")[:100]})
            time.sleep(1)
        cell = {}
        for t in trials:
            if not t["picked"]:
                continue
            k = f'{t["block"]}|{t["arm"]}'
            c = cell.setdefault(k, [0, 0])
            c[1] += 1
            c[0] += bool(t["picked_target"])
        all_results[label] = {"trials": trials,
                              "cells": {k: {"hits": v[0], "n": v[1],
                                            "p": round(v[0] / v[1], 3)} for k, v in sorted(cell.items())}}
        print("   " + json.dumps(all_results[label]["cells"]), flush=True)

    out = f"{outdir}/RUN_{stamp}.json"
    json.dump({"spec": spec, "results": all_results}, open(out, "w"), indent=1)
    print(f"saved {out}")
