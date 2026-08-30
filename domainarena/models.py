"""Implementation scaffold: canonical DomainArena product types.

Copy/adapt into the existing repo after reconciling with current AgentSEOLab models.
"""
from __future__ import annotations
from typing import Literal, Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator

Audience = Literal["consumer", "business", "developer", "ai_agent"]

class ConstraintSet(BaseModel):
    max_purchase_price: float | None = Field(default=None, ge=0)
    max_renewal_price: float | None = Field(default=None, ge=0)
    premium_allowed: bool = False
    allowed_tlds: list[str] = Field(default_factory=lambda: ["com", "dev", "io"])
    purchase_types: list[str] = Field(default_factory=lambda: ["registration"])
    max_length: int | None = Field(default=None, ge=1, le=63)
    hyphens_allowed: bool = False
    digits_allowed: bool = False

class DomainIntent(BaseModel):
    description: str
    primary_job: str
    objects: list[str] = Field(default_factory=list)
    desired_associations: list[str] = Field(default_factory=list)
    prohibited_meanings: list[str] = Field(default_factory=list)
    current_category: str | None = None
    adjacent_categories: list[str] = Field(default_factory=list)
    audiences: list[Audience]
    constraints: ConstraintSet

class InventorySnapshot(BaseModel):
    domain_name: str
    sld: str
    tld: str
    purchasable: bool
    premium: bool = False
    purchase_price: float | None = None
    renewal_price: float | None = None
    purchase_type: str | None = None
    reason: str | None = None
    checked_at: str

class Candidate(BaseModel):
    candidate_id: str
    domain_name: str
    generator: str
    generation: int = 0
    parent_ids: list[str] = Field(default_factory=list)
    inventory: InventorySnapshot

class EvStatus(str, Enum):
    MEASURED = "MEASURED"
    PROXY = "PROXY"
    NOT_MEASURED = "NOT_MEASURED"


class EvidenceValue(BaseModel):
    """A single evidence dimension with explicit provenance (peer review §3.1).
    Never present a structural proxy as a measured quantity."""
    value: float | None = None
    status: EvStatus = EvStatus.NOT_MEASURED
    protocol: str | None = None      # e.g. DA-T2-v2 / DA-T6
    n: int | None = None
    note: str | None = None


def _coerce_evidence(v):
    """Backward-compat: bare floats become PROXY-valued evidence."""
    if isinstance(v, (int, float)):
        return EvidenceValue(value=float(v), status=EvStatus.PROXY,
                             note="bare float coerced as PROXY")
    return v

class EvidenceVector(BaseModel):
    @field_validator("semantic_transmission", "pairwise_strength",
                     "structural_fluency_proxy", "worst_family",
                     "task_success", "human_recall", "brand_elasticity",
                     mode="before")
    @classmethod
    def _wrap_floats(cls, v):
        return _coerce_evidence(v)

    semantic_transmission: EvidenceValue = EvidenceValue()
    pairwise_strength: EvidenceValue = EvidenceValue()
    structural_fluency_proxy: EvidenceValue = EvidenceValue(
        status=EvStatus.PROXY)
    worst_family: EvidenceValue = EvidenceValue()
    task_success: EvidenceValue = EvidenceValue()
    human_recall: EvidenceValue = EvidenceValue()
    brand_elasticity: EvidenceValue = EvidenceValue()
    evaluator_coverage: str | None = None

class RecommendationDecision(BaseModel):
    decision_id: str
    intent_hash: str
    recommended_candidate_id: str
    pareto_candidate_ids: list[str]
    policy_version: str
    evidence: EvidenceVector
    purchase_requires_approval: bool = True
    approval_token: str | None = None  # set on approval, required for registration
