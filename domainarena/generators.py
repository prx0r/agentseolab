"""Heterogeneous candidate generation + live inventory intersection.

Generator families (cheap, deterministic unless an LLM family is enabled):
  - keyword compounds from the frozen intent
  - descriptive function names (verb+noun)
  - brandable neologisms (syllable blends)
  - name.com Search inventory as a generator itself (sponsor-native)

Output target: 100-200 raw -> ~30 feasible after constraints ∩ inventory.
"""
from __future__ import annotations
import itertools
import re

from .intent import keywords_from_intent
from .models import Candidate, ConstraintSet, DomainIntent, InventorySnapshot

FUNCTION_VERBS = ["check", "verify", "probe", "repair", "fetch", "parse", "scan",
                  "trace", "guard", "audit"]
FUNCTION_NOUNS = ["api", "dev", "hub", "lab", "bot", "kit", "base", "works"]
BRAND_SYLLABLES_A = ["ve", "lo", "fa", "no", "zi", "ka", "mi", "ta"]
BRAND_SYLLABLES_B = ["lora", "nova", "bit", "flux", "gen", "pilot", "forge", "wave"]


def _mk(cand_id: str, domain: str, generator: str) -> Candidate:
    sld, _, tld = domain.partition(".")
    return Candidate(candidate_id=cand_id, domain_name=domain,
                     generator=generator,
                     inventory=InventorySnapshot(
                         domain_name=domain, sld=sld, tld=tld,
                         purchasable=False, checked_at="unverified"))


def generate_candidates(intent: DomainIntent, limit: int = 200) -> list[Candidate]:
    kws = keywords_from_intent(intent)[:6]
    out: list[Candidate] = []
    seen: set[str] = set()

    def add(domain: str, gen: str):
        if domain not in seen and len(out) < limit:
            seen.add(domain)
            out.append(_mk(f"{gen}_{len(out)}", domain, gen))

    # keyword compounds × TLDs
    for a, b in itertools.permutations(kws, 2):
        for tld in intent.constraints.allowed_tlds[:3]:
            add(f"{a}{b}.{tld}", "kw_compound")
    # verb+noun function names
    for v in FUNCTION_VERBS:
        for n in FUNCTION_NOUNS[:4]:
            add(f"{v}{n}.com", "function_name")
            add(f"{v}-{n}.dev", "function_name") if intent.constraints.hyphens_allowed else None
    # brandable blends
    for a in BRAND_SYLLABLES_A:
        for b in BRAND_SYLLABLES_B:
            add(f"{a}{b}.com" if len(a + b) <= 10 else f"{a}{b}.io", "brandable")
    return out


def intersect_inventory(candidates: list[Candidate],
                        snaps: list[InventorySnapshot]) -> list[Candidate]:
    """Attach real name.com snapshots; drop candidates not found in inventory."""
    by_name = {s.domain_name.lower(): s for s in snaps}
    kept = []
    for c in candidates:
        snap = by_name.get(c.domain_name.lower())
        if snap is None:
            continue
        c.inventory = snap
        kept.append(c)
    return kept
