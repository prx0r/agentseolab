"""Implementation scaffold: canonical DomainArena product types.

Copy/adapt into the existing repo after reconciling with current AgentSEOLab models.
"""
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field

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

class EvidenceVector(BaseModel):
    semantic_transmission: float | None = None
    pairwise_strength: float | None = None
    model_stability: float | None = None
    worst_family: float | None = None
    task_success: float | None = None
    human_recall: float | None = None
    brand_elasticity: float | None = None
    evaluator_coverage: str | None = None

class RecommendationDecision(BaseModel):
    decision_id: str
    intent_hash: str
    recommended_candidate_id: str
    pareto_candidate_ids: list[str]
    policy_version: str
    evidence: EvidenceVector
    purchase_requires_approval: bool = True
