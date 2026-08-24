"""Canonical DomainArena intent: frozen and hash-locked before generation."""
from __future__ import annotations
import hashlib
import json
import re
from datetime import datetime, timezone

from .models import Audience, ConstraintSet, DomainIntent

DEFAULT_CONSTRAINT = ConstraintSet()


def freeze_intent(
    description: str,
    primary_job: str,
    audiences: list[Audience],
    constraints: ConstraintSet | None = None,
    **kwargs,
) -> tuple[DomainIntent, str]:
    intent = DomainIntent(
        description=description.strip(),
        primary_job=primary_job.strip(),
        audiences=audiences,
        constraints=constraints or DEFAULT_CONSTRAINT,
        **kwargs,
    )
    return intent, intent_hash(intent)


def intent_hash(intent: DomainIntent) -> str:
    payload = json.dumps(
        intent.model_dump(exclude_none=True), sort_keys=True, separators=(",", ":")
    ).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def keywords_from_intent(intent: DomainIntent) -> list[str]:
    """Extract candidate keyword roots from the frozen intent (deterministic)."""
    words = re.findall(r"[a-z][a-z0-9]+", (intent.description + " " + intent.primary_job).lower())
    stop = {
        "the", "a", "an", "for", "and", "with", "that", "this", "of", "to", "in",
        "on", "by", "is", "are", "be", "it", "as", "at", "or", "from", "which",
    }
    seen: list[str] = []
    for w in words:
        if w not in stop and w not in seen and len(w) >= 3:
            seen.append(w)
    return seen


def new_decision_id() -> str:
    return "da_" + hashlib.sha256(
        datetime.now(timezone.utc).isoformat().encode()
    ).hexdigest()[:16]
