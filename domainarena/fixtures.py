"""Canonical hardcoded fixtures — real prior AgentSEOLab results, frozen.

Source: results/ledger/evidence.json via RESULTS.md snapshot 2026-08-23.
These are the deterministic demo/regression fixtures: the pipeline must
reproduce these shapes offline without any network access.

NEVER edit numbers by hand; they are evidence, not decoration. If a rerun
disagrees, the disagreement is the finding (H-SERVE01 discipline).
"""
from __future__ import annotations

# H-ASL001a/b — working-vs-fluffy selection, per family (protocol v2)
ASL001_FAMILY_PICKS = {
    "mistral-small-24b": {"p": 1.0, "n": 30, "cluster": "resistant"},
    "ox-alpha-free": {"p": 0.929, "n": 28, "cluster": "resistant"},
    "nemotron-super-120b": {"p": 0.7, "n": 30, "cluster": "resistant"},
    "llama-3.3-70b": {"p": 0.367, "n": 30, "cluster": "seduced"},
    "qwen3-30b": {"p": 0.172, "n": 29, "cluster": "seduced"},
    "gemma-4-26b": {"p": 0.138, "n": 29, "cluster": "seduced"},
    "gpt-oss-20b": {"p": 0.0, "n": 30, "cluster": "seduced"},
}

# H-ASL002C — symmetric fluff collapses every family to exactly chance
ASL002C_FLUFF_BOTH = {
    "meta-llama-3.3-70b": 0.50,
    "mistral-small-24b": 0.50,
    "qwen3-30b": 0.50,
    "gpt-oss-20b": 0.50,
}

# H-TLD01 — position-stratified P(pick | slot) — the CORRECTED estimands
TLD01_P_PICK_GIVEN_POS0 = {
    ".com": (29, 29),
    ".org": (18, 19),
    ".dev": (22, 28),
    ".io": (21, 26),
    ".xyz": (17, 21),
}
TLD01_OFF_POS0_COM = (14, 94)          # residual .com preference off top slot
TLD01_POSITION_PRIMACY_P = 0.87        # raw share of slot-1 picks, n=123 decided

# H-NAMING01 — ceiling null: name style irrelevant under informative descriptions
NAMING01_CEILING = {"families": 6, "trials_per_family": 36, "target_picked": 215, "n": 216}

# Demo fixture intents (deterministic showcase set)
DEMO_INTENTS = [
    {
        "description": "Repairs malformed JSON for AI agents",
        "primary_job": "repair JSON",
        "audience": "ai_agent",
        "max_purchase_price": 20.0,
    },
    {
        "description": "Verifies citations and factual claims in text",
        "primary_job": "verify citations",
        "audience": "developer",
        "max_purchase_price": 20.0,
    },
]

DEMO_CANDIDATES = [
    # domain, purchase, renewal, semantic, stability, worst_family, task_success
    ("jsonrepair.dev", 9.99, 11.99, 0.92, 0.84, 0.71, 0.88),
    ("factprobe.dev", 12.99, 14.99, 0.81, 0.86, 0.78, 0.83),
    ("velora.com", 10.44, 12.88, 0.31, 0.62, 0.39, 0.44),
]
