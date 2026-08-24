"""CP6 — Cross-family + cross-serving-window robustness.

H-SERVE01 (CONFIRMED): serverless temp=0 flips behaviour across time windows.
Therefore family classifications are UNSTABLE until ≥2 windows agree, and the
worst-family outcome is reported separately from the mean. Never pool before
testing homogeneity (H-ASL001b: seduced vs resistant clusters).
"""
from __future__ import annotations
import statistics
from dataclasses import dataclass


@dataclass
class FamilyOutcome:
    family: str
    window_id: str
    p_task_verified: float
    n: int


def per_family_matrix(outcomes: list[FamilyOutcome]) -> dict[str, dict]:
    by_family: dict[str, list[FamilyOutcome]] = {}
    for o in outcomes:
        by_family.setdefault(o.family, []).append(o)
    matrix = {}
    for fam, runs in sorted(by_family.items()):
        ps = [r.p_task_verified for r in runs]
        ns = [r.n for r in runs]
        stable = len(ps) >= 2 and max(ps) - min(ps) <= 0.15 and all(n >= 30 for n in ns)
        matrix[fam] = {
            "windows": {r.window_id: r.p_task_verified for r in runs},
            "mean": statistics.fmean(ps),
            "range": max(ps) - min(ps),
            "variance": statistics.pvariance(ps) if len(ps) > 1 else 0.0,
            "min_n": min(ns),
            "stable": stable,
        }
    return matrix


def robustness_report(outcomes: list[FamilyOutcome]) -> dict:
    matrix = per_family_matrix(outcomes)
    if not matrix:
        return {"families": 0}
    means = {fam: m["mean"] for fam, m in matrix.items()}
    worst = min(means, key=means.get)
    stable_fams = [f for f, m in matrix.items() if m["stable"]]
    pooled = [o.p_task_verified for o in outcomes if o.family in stable_fams] or \
             [o.p_task_verified for o in outcomes]
    return {
        "families": len(matrix),
        "stable_families": len(stable_fams),
        "unstable_families": len(matrix) - len(stable_fams),
        "mean_of_family_means": statistics.fmean(means.values()),
        "range_across_families": max(means.values()) - min(means.values()),
        "variance_across_families": statistics.pvariance(list(means.values()))
                                    if len(means) > 1 else 0.0,
        "worst_family": worst,
        "worst_family_mean": means[worst],
        # serving coverage: fraction of families with multi-window replication
        "serving_coverage": len(stable_fams) / len(matrix),
        "pooled_healthy_p": statistics.fmean(pooled),
    }


def healthy_families(min_n: int = 20, families_available: list[str] | None = None,
                     dead: set[str] | None = None) -> list[str]:
    """Families eligible for replication runs (AGENTS.md model policy)."""
    available = families_available or [
        "@cf/meta/llama-3.3-70b-instruct-fp8-fast",
        "@cf/mistralai/mistral-small-3.1-24b-instruct",
        "@cf/qwen/qwen3-30b-a3b-fp8",
        "@cf/openai/gpt-oss-20b",
        "@cf/google/gemma-4-26b-a4b-it",
    ]
    return [f for f in available if f not in (dead or set())]
