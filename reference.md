# Reference: The Agent Economy Architecture
*(2026-08-23 · saved from strategy review — see also abuse.md for AgentSEOLab operating plan)*

## Core reframing
Not "AI agents as app category" but: **infrastructure letting autonomous software discover opportunities, choose counterparties/tools, obtain authority, spend resources, execute work, prove what happened, and improve.** Model intelligence is commoditizing; hard problems move outside the model.

## The stack
Discover (AgentSEO) → Describe (Agent Cards/WebMCP) → Interact (MCP/A2A v1.0) → Choose (routing/LLMDeals) → Authorize (AP2 mandates ≠ wallet) → Pay (x402/AP2) → Execute (factories/Cogym) → Verify (Work Receipts) → Reputation (receipt-derived) → Learn (Cogym) → Route again.

Key standards shift: A2A v1.0 (Agent Cards at /.well-known/agent-card.json), MCP 2026-07-28 spec (long-running tasks + authorization), Chrome WebMCP (typed actions to browser agents — actuation accuracy over visual inference).

**AgentSEO endgame = optimization unit is the machine-addressable capability, not the web page.** Internal name candidate: Agent Discovery Science / Machine Addressability.

## The receipt convergence
Independently reinvented across projects: Work Receipt / Proof-of-Work / ATRP. ERC-8004 gives identity/reputation/validation registries but ecosystem is "registration-heavy, operationally shallow" — sparse evidence of completed economic activity. That's the hole: receipts→reputation, not self-declared reputation→trust.
Receipt shape: actor, requester, task, input_commitment, capability_used, mandate(budget/quoted/actual price), times, artifacts[], tests[], validator_results[], outcome, reward/failure_reason, previous_receipts[], skill_version, signatures[].

## Cogym ∘ AgentSEO composition
Synthetic economy: 100 services (weather APIs, research agents, scrapers, LLMs, escalation...) each with price/latency/advertised-vs-true capabilities/maliciousness/history. Release agents with $10 budget, 20 tasks, partial info. Measure: what discovered/trusted/paid; advertised-vs-reality match rate; do receipts improve routing; reputation farming detectable; does experience improve decisions.
Research questions: receipt-rep > stars? task-specific rep > global? verified rep > self-reported? recency weighting?
= **an experimental internet for autonomous agents.** Output dataset simultaneously = AgentSEO data + reputation data + routing data + eval data + Cogym training data.

## Decision-loop summary
identity(WHO) · capability(WHAT can) · mandate(WHAT allowed) · wallet(WHAT pays) · receipt(WHAT did) · reputation(WHAT happened before).
Discovery → Decision → Authorization → Execution → Receipt → Learning → loop.

## Moat
Not another agent framework (A2A/MCP commoditize that). It is the **evidence graph of millions of agent decisions**: agent X met options A/B/C in context Y, chose B on signals P/Q, spent $0.014, artifact Z scored 0.93, user accepted → future agents shift toward B.

## Watch list
A2A spec versions, MCP spec releases, WebMCP, ERC-8004 adoption, AP2 mandates, self-improving-agent research (trajectory memory, SkillMaster-style skill refinement).
