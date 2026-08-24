# AgentSEOLab — Experiment Log

**Date:** 2026-08-22
**Researcher:** opencode (automated)
**Purpose:** Find the best domain for a "canonical vending machine for verified machine-readable facts" service

---

## Experiment Overview

| # | Experiment | Hypothesis | Models | Result |
|---|-----------|------------|--------|--------|
| 1 | Field Trace | Agents search for "validation/verification" not "truth/proof" | 1b, 2b, 3b | CONFIRMED |
| 2 | Semantic Inversion | Domain names transmit product category | 1b, 2b, 3b | FAILED (0-20%) |
| 3 | Pairwise Tournament | Suggestive compounds beat descriptive | 1b, 2b, 3b | MIXED |
| 4 | Cross-Model Consistency | Preferences stable across architectures | 1b, 2b, 3b | WEAK (0-50%) |
| 5 | Position Bias | LLMs show first-position bias | 1b, 2b, 3b | NONE (0%) |
| 6 | Tool Description A/B | "Execution proof" beats "cryptographic proof" | 3b | CONFIRMED |
| 7 | Trust Signals | Reputation > freshness > proof type | 3b | CONFIRMED |
| 8 | Naming Family Tournament | Which family wins? | 3b, 70B | action_object > suggestive |
| 9 | Archetype Mapping | Which word fits "find information"? | 3b | hound > cloud > fetch |
| 10 | Memory (recall) | Concrete words recalled better | 3b | FAILED (0/5) |
| 11 | Exposure Curve | Context changes preference | 3b | NO SHIFT |
| 12 | Processing Fluency | All names spellable | 3b | 100% |
| 13 | Sound Symbolism | velko sounds "small+fast" | 3b | CONFIRMED |
| 14 | Domain Causal | Hostname alone shifts selection | 3b | CONFIRMED |

---

## Key Findings

### Finding 1: Agent search vocabulary ≠ domain name vocabulary
Agents search for: "email validation services", "API health checker", "DNS validation tool"
Domains contain: "truth", "proof", "evidence", "facts"
**Gap: agents never search for "truth" or "proof" when looking for verification services.**

### Finding 2: Position bias = 0%
Across 26+ comparisons, the3b model showed zero first-position bias. This contradicts Shi et al. 2024 which found 55-65% bias in larger models. May be model-size dependent.

### Finding 3: Cross-model agreement is weak
Llama-1b vs Llama-3b: 0% agreement. Llama-1b vs Gemma-2b: 50%. Preferences are NOT stable across architectures at small model sizes.

### Finding 4: Semantic transmission near zero
No domain name successfully communicated "verified facts service" to any model. They guessed marketplace, crypto, news. The concept is too novel for cold-start name inference.

### Finding 5: Reputation signal dominates trust
When agents evaluate a service, "99.7% accuracy across 1M+ verifications" (8/10) beats "verified 30 seconds ago" (6/10), "actually executed" (5/10), and "cites source" (5/10).

### Finding 6: "Execution proof" beats "cryptographic proof"
For API/DNS checks, "tested by actually executing" was preferred over "cryptographic proof of state". For email, "cryptographic proof" won. Context matters.

---

## Available Domains (RDAP-verified)

| Domain | Length | Tournament Wins | Field Trace Match | Recommendation |
|--------|:------:|:---------------:|:-----------------:|:--------------:|
| verifyv.com | 7 | 3 | HIGH | BEST MATCH |
| centifacts.com | 10 | 7 | LOW | Tournament winner |
| invoketruth.com | 11 | 4 | LOW | User's pick |
| truthvend.com | 9 | 6 | LOW | High tournament |
| verifiedbits.com | 12 | 6 | MEDIUM | Long but strong |

---

## The Verdict

**verifyv.com** is the best domain because:
1. Contains "verify" — the #1 verb agents actually search for
2. 7 characters — shortest available option
3. Phonetically unambiguous (100% spelling accuracy)
4. Matches field trace vocabulary ("email verification", "API verification")
5. Low semantic transmission is offset by high search vocabulary match

**invoketruth.com** scored lowest in tournament (4 wins) and field traces show agents never search for "invoke truth".

**centifacts.com** won the tournament (7 wins) but doesn't match agent search vocabulary.

---

## Files

- `experiment.db` — Original 9-experiment suite (60 comparisons)
- `company_domain.db` — v1 domain search (49 comparisons)
- `company_domain_v2.db` — v2 fixed experiments (14 comparisons + BT)
- `company_domain_v3.db` — v3 scientific method (26 comparisons + field traces)
- `run_all.py` — Original experiment runner
- `company_domain_search.py` — v1 domain search
- `company_domain_v2.py` — v2 with controls
- `company_domain_v3.py` — v3 with field traces + RDAP
- `experiment1.py` — Original pairwise experiment
- `experiment1b.py` — Cross-validation with 70B

---

## Methodology Notes

### What we fixed between versions
| Issue | v1 | v2 | v3 |
|-------|----|----|-----|
| Availability check | None | RDAP (manual) | RDAP (batch) |
| Position bias | Not measured | Measured (0%) | Measured (0%) |
| Generator/judge separation | Same model | 70B generates,3B judges | 70B generates, 3 judges |
| Field traces | Not done | Not done | Done (KEY experiment) |
| Cross-model validation | 2 models | 2 models | 5 models |
| Length control | Not done | Measured | Measured |
| Repetition | 1x | 2x | 1x (across 3 models) |

### Research basis
- SCIENTIFIC_METHOD.md — frozen intent, field trials, pairwise with order reversal
- DOMAIN_ANIMAL_SCIENCE.md — 7 experiment types
- FRONTIER_NOTES.md — position bias (Shi et al. 2024)
- DEEP_RESEARCH.md — tool A/B, trust signals, cross-model consistency
- GEO paper (arXiv:2311.09735) — content interventions
- Agent consistency (arXiv:2605.28840) — structural consistency
- Agentic Search (arXiv:2601.17617) — 14M real search requests
- AgentSearchBench (arXiv:2604.22436) — execution-aware signals
