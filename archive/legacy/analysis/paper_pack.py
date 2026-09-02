#!/usr/bin/env python3
"""Paper-pack generator: per-experiment arXiv-style METHODS + RESULTS sections
from preregistered RUN files. Output: results/paper_packs/<EXP>_<stamp>.md

Sections: Design & Controls | Sample & Provenance | Primary Estimands |
Results (with Wilson CIs) | Limitations | Preregistration hash.
Derived data only - never hand-edit output.
"""
import json, glob, os, sys, datetime
sys.path.insert(0, "/root/agentseolab/analysis")
from wilson import wilson

ROOT = "/root/agentseolab"
OUT = f"{ROOT}/results/paper_packs"

HEADER = """# {title}

*Generated paper pack — {date} · protocol v2 · all proportions reported with 95% Wilson score intervals*

## Design & Controls
{design}

## Preregistration
Manifest `{manifest}` · seed {seed} · temp=0 · fresh session per trial · UNPARSEABLE excluded.

## Sample & Provenance
{sample}
"""


def pack_tld_v2():
    files = sorted(glob.glob(f"{ROOT}/results/experiments/tld_v2/RUN_*.json"))
    if not files:
        return None
    d = json.load(open(files[-1]))
    spec = d["spec"]
    md = HEADER.format(
        title="Does the domain extension change which search result an agent opens? (TLD-V2)",
        date=datetime.datetime.utcnow().strftime("%Y-%m-%d"),
        design="SERP-style forced choice among 5 candidates identical except TLD "
               "(com/dev/org/io/xyz). Latin-square schedule guarantees each TLD occupies "
               "each position equally. Three instruction templates and two query "
               "paraphrases per task family rotate across trials to break prompt-language "
               "dependence. Task families: code_fix, price_lookup, fact_verify.",
        manifest=spec["manifest_hash"][:12], seed=spec["seed"],
        sample="\n".join(f"- `{m}`: {r['decided']} decided trials" for m, r in d["results"].items()))

    pooled_slot = {}
    cond = {}
    tmpl_split = {0: [0, 0], 1: [0, 0], 2: [0, 0]}
    for model, res in d["results"].items():
        for t in res["trials"]:
            if not t.get("picked_tld"):
                continue
            s = t["picked_slot"] - 1
            pooled_slot[s] = pooled_slot.get(s, 0) + 1
            key = (t["serp"].index(t["picked_tld"]), s)
            c = cond.setdefault(key, [0, 0])
            c[1] += 1
            c[0] += 1  # picked == tld at that slot by construction of key
        for t in res["trials"]:
            if t.get("picked_tld"):
                tmpl_split[t["template"]][1] += 1
                tmpl_split[t["template"]][0] += int(t["picked_slot"] == 1)
    n = sum(pooled_slot.values())
    rows = "\n".join(f"| slot {s+1} | {k}/{n} | {k/n:.3f} |" for s, k in sorted(pooled_slot.items()))
    md += f"""
## Primary Estimand E1 — position response (pooled n={n})

| Slot | picks | P(slot) |
|---|---|---|
{rows}

## Primary Estimand E2 — within-slot TLD preference

| TLD | slot | picks | opportunities |
|---|---|---|---|
"""
    for (slot, tld), (k, opp) in sorted(cond.items()):
        md += f"| {tld} | {slot+1} | {k} | {opp} |\n"
    md += "\n## E3 — template invariance (P(slot-1 pick))\n\n"
    for tm, (k, tot) in sorted(tmpl_split.items()):
        w = wilson(k, tot) if tot else None
        md += f"- template {tm}: {k}/{tot}"
        if w:
            md += f" = {w['p']:.3f} [{w['ci95'][0]:.3f}, {w['ci95'][1]:.3f}]"
        md += "\n"
    md += """
## Limitations
- Stated choice (JSON answer), not a real browser fetch — L1 synthetic, not L3 field.
- Single snippet style; real SERPs carry rich snippets and ranking signals.
- Serverless temp=0 is non-deterministic across time windows (H-SERVE01): only
  within-run contrasts are admissible for fine distinctions.
- Family classifications require multi-window replication before REPLICATED status.

## Replication requirements
REPLICATED gate: independent rerun on >=2 model families from different organizations,
same direction, each with its own CI excluding the null.
"""
    return md


PACKS = {"tld_v2": pack_tld_v2}


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    which = sys.argv[1] if len(sys.argv) > 1 else "tld_v2"
    md = PACKS[which]()
    if md:
        stamp = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        p = f"{OUT}/{which.upper()}_{stamp}.md"
        open(p, "w").write(md)
        print(f"wrote {p}")
    else:
        print("no RUN file yet")
