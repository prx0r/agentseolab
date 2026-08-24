"""Audience-conditioned decision policy scaffold.

Hard constraints are applied before this module. These weights choose among feasible/Pareto
candidates and are policy choices, not scientific truths.
"""
PRESETS = {
    "agent_api": {
        "semantic_transmission": 0.25,
        "task_success": 0.25,
        "pairwise_strength": 0.15,
        "structural_fluency_proxy": 0.20,
        "brand_elasticity": 0.05,
        "human_recall": 0.00,
        "worst_family": 0.10,
    },
    "developer": {
        "semantic_transmission": 0.22,
        "task_success": 0.18,
        "pairwise_strength": 0.14,
        "structural_fluency_proxy": 0.16,
        "brand_elasticity": 0.10,
        "human_recall": 0.10,
        "worst_family": 0.10,
    },
    "consumer": {
        "semantic_transmission": 0.15,
        "task_success": 0.05,
        "pairwise_strength": 0.10,
        "structural_fluency_proxy": 0.10,
        "brand_elasticity": 0.20,
        "human_recall": 0.30,
        "worst_family": 0.10,
    },
}
