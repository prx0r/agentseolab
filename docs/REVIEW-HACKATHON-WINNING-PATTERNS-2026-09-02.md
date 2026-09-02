# DomainArena — Honest Peer Review vs Winning Patterns

**Date:** 2026-09-02
**Reviewer:** opencode (mimo-v2.5)
**Context:** Hackathon deadline Sept 3. DevNetwork API + Cloud + AI, name.com track.

---

## Scorecard vs winning patterns

| Pattern | DomainArena has it? | Score | Notes |
|---------|---------------------|-------|-------|
| **Magic transition** | Partial | 6/10 | The transition "intent → registered domain" is magic, but the demo currently stops at recommendation in fixture mode. Registration/DNS requires name.com creds we don't have. |
| **Action, not answer** | Partial | 5/10 | The API supports register + DNS, but the demo UI doesn't walk through it. A judge clicking "try it" sees recommendation only. |
| **Before/after** | No | 3/10 | No "before" state shown. No comparison between naive domain pick and agent-tested winner. |
| **Sponsor causally necessary** | Yes (in code) | 7/10 | name.com is used for search, availability, pricing, registration, DNS. But the demo doesn't make this visible — it's buried in the API. |
| **Looks like a product** | No | 4/10 | 22 .md files at root, stray scripts, no LICENSE, no clear "run this" path. Looks like a research dump. |
| **One-sentence problem** | Yes | 9/10 | "A/B testing for domain names in the agentic web" is excellent. |
| **Satisfying before/after** | No | 2/10 | No visual before/after. No "this domain failed, this one passed." |
| **Human proof** | Partial | 6/10 | The concept is immediately understandable. But the demo doesn't show it happening. |
| **Sponsor proof** | Yes (in tests) | 7/10 | 6 name.com endpoints used. Tests prove it. But judges don't read tests. |
| **Engineering proof** | Yes | 9/10 | 148 tests, Wilson CI, AB/BA randomization, cross-family. Strong. |

**Overall: 6.8/10** — Strong concept, weak presentation.

---

## The three things that would move this to 9/10

### 1. Make the demo walk through registration (even if mocked)

The demo currently shows: intent → candidates → recommendation → done.

It needs to show: intent → candidates → recommendation → **availability check → approval → register → DNS → receipt**.

Even if name.com is mocked in fixture mode, the UI should walk through all 8 steps with visual feedback at each step.

### 2. Add a "before/after" comparison screen

Show:
```
Human pick:     jsonultra.xyz    → agent thinks "fantasy game"    → WRONG
Agent-tested:   fixjson.com      → agent thinks "JSON repair"     → CORRECT
```

This is the memorable moment. A judge tells another judge about this.

### 3. Clean the repo root

22 .md files at root is disqualifying for "looks like a product." Move everything except README.md, DEMO.md, LICENSE to docs/ or archive/.

---

## What's actually strong (don't weaken these)

- **One-line pitch**: "A/B testing for domain names in the agentic web" — perfect
- **name.com integration depth**: 6 endpoints, real lifecycle — strongest sponsor integration in the hackathon
- **Research foundation**: 16 experiments, 7+ model families — genuine novelty
- **Test suite**: 148/148, lifecycle tests, write guard — engineering credibility
- **Write guard**: DOMAINARENA_ALLOW_WRITES=1 — shows maturity with irreversible actions

---

## Refinement plan (ordered by impact)

### TODAY (before submission)

| Priority | Task | Impact | Effort |
|----------|------|--------|--------|
| P0 | Clean repo root: move 20 .md files to docs/ | HIGH | 15 min |
| P0 | Add LICENSE file (MIT) | HIGH | 2 min |
| P0 | Add "Full lifecycle verified" section to README showing test output | HIGH | 10 min |
| P1 | Update demo UI to show all 8 steps (even if steps 5-8 are fixture/mocked) | HIGH | 1 hr |
| P1 | Add before/after comparison screen to demo | HIGH | 30 min |
| P1 | Fix CI (GitHub Actions red) | HIGH | 30 min |

### TOMORROW (demo day)

| Priority | Task | Impact | Effort |
|----------|------|--------|--------|
| P1 | Get name.com sandbox credentials from Devpost | CRITICAL | 30 min |
| P1 | Run full lifecycle with real name.com sandbox | CRITICAL | 1 hr |
| P1 | Record 2:30 video: intent → agents test → register → DNS → receipt | CRITICAL | 2 hr |
| P2 | Screenshot final receipt for Devpost | MEDIUM | 5 min |
| P2 | Fill Devpost fields | MEDIUM | 30 min |

### AFTER submission (if time)

| Priority | Task | Impact | Effort |
|----------|------|--------|--------|
| P2 | Agent Legibility Lab page | MEDIUM | 2 hr |
| P2 | Price-vs-legibility frontier chart | LOW | 1 hr |

---

## The demo script (revised per winning patterns)

### 0:00-0:12 — Hook
> "Domain search tools tell humans which names sound good. But increasingly the customer discovering your service is an AI agent — and nobody measures whether the agent understands your domain at all."

### 0:12-0:25 — Product statement
> "DomainArena experimentally tests live available domains against multiple AI agents, then name.com acquires and configures the winner."

### 0:25-1:55 — The magic trick (uninterrupted)
```
type intent
↓
name.com live candidates appear
↓
blind agent interpretations
↓
one obviously wrong interpretation
↓
cross-model comparison
↓
winner selected
↓
fresh availability/price
↓
approve
↓
register
↓
DNS
↓
readback
```

### 1:55-2:20 — Sponsor proof
```
API TRACE
POST domains:search       200  182ms
POST checkAvailability    200  107ms
GET  getPricing           200   94ms
POST domains              200  241ms
POST records              200  121ms
GET  records              200   88ms
```
> "name.com isn't a checkout button bolted on at the end. It provides the inventory, constraints, execution and verification throughout the workflow."

### 2:20-2:40 — One technical wow
> "Underneath the product is an experimental program across seven model families. Instead of trusting one LLM rating, we treat domain quality as something we can actually measure."

### 2:40-2:55 — Startup extension
> "Today we measure names before purchase. Tomorrow the same score becomes an agent-legibility signal for registrars, registries, and the machine-readable web."

### 2:55-3:00 — Final image
```
REGISTERED
DNS VERIFIED

domain: fixjson.com
```

---

## The one sentence (for Devpost)

> "It's the one that A/B tests available domain names on AI agents and then literally buys/configures the winner."

## The three levels of proof

**Level 1 (human):** Agents understand one domain better than another.
**Level 2 (sponsor):** name.com provides inventory, constraints, execution, and verification throughout.
**Level 3 (engineering):** 148 tests, Wilson CI, AB/BA randomization, cross-family replication, write guards.
