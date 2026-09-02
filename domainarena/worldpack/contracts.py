"""Local contracts — self-contained types for DomainArena world protocol.

These replace the cogym_kernel dependency with minimal local definitions.
Copied from cogym_kernel/kernel/contracts.py with provenance noted.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Literal


def content_id(prefix: str, obj: Any) -> str:
    """Deterministic id: prefix + '_' + hex digest of canonical JSON."""
    def _strip_volatile(o: Any) -> Any:
        if isinstance(o, dict):
            return {k: _strip_volatile(v) for k, v in o.items()
                    if k not in ("created_at", "updated_at", "timestamp")}
        if isinstance(o, (list, tuple)):
            return [_strip_volatile(i) for i in o]
        return o
    raw = json.dumps(_strip_volatile(obj), sort_keys=True, default=str)
    h = hashlib.sha256(raw.encode()).hexdigest()[:32]
    return f"{prefix}_{h}"


@dataclass(frozen=True)
class WorldSpec:
    world_kind: str
    version: str
    instance_set_hash: str
    environment_hash: str
    oracle_hash: str
    metadata: dict = field(default_factory=dict)

    @property
    def spec_id(self) -> str:
        return content_id("worldspec", self)


@dataclass(frozen=True)
class ActionSpec:
    kind: str
    payload: dict = field(default_factory=dict)
    executor_kind: str = "deterministic"
    estimated_cost: float | None = None
    timeout_ms: int | None = None
    metadata: dict = field(default_factory=dict)

    @property
    def action_id(self) -> str:
        return content_id("action", {"kind": self.kind, "payload": self.payload})


@dataclass(frozen=True)
class ActionResult:
    action_id: str
    status: Literal["ok", "error", "timeout"]
    payload: dict = field(default_factory=dict)
    started_ns: int = 0
    finished_ns: int = 0
    wall_ms: float = 0.0
    cash_cost: float = 0.0
    normalized_cost: float = 0.0
    provider: str = ""
    request_hash: str = ""


@dataclass(frozen=True)
class Metric:
    name: str
    value: float
    direction: Literal["min", "max"] = "max"


@dataclass(frozen=True)
class MetricVector:
    metrics: tuple[Metric, ...] = ()

    def get(self, name: str) -> float | None:
        return next((m.value for m in self.metrics if m.name == name), None)

    def names(self) -> tuple[str, ...]:
        return tuple(m.name for m in self.metrics)


@dataclass(frozen=True)
class CandidateArtifact:
    kind: str
    version: str
    config: dict
    parent_ids: tuple[str, ...] = ()
    provenance: dict = field(default_factory=dict)


@dataclass(frozen=True)
class RunReceipt:
    run_id: str
    world_spec_id: str
    worker_version: str
    events: tuple[dict, ...] = ()
    artifacts: tuple[str, ...] = ()
    metrics: MetricVector = field(default_factory=MetricVector)
    total_cost: float = 0.0
    wall_ms: float = 0.0
    success: bool = False
    metadata: dict = field(default_factory=dict)

    @property
    def receipt_id(self) -> str:
        return content_id("receipt", self)
