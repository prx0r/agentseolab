# VERIF — Do verification signals raise agent click-through?

## Causal Question
When search/tool candidates are otherwise identical, do verification markers in the
snippet ("verified today", "provenance receipt available", "audited", "open-source,
self-hostable") increase agent SELECTION? Does the effect scale with TASK STAKES
(low-stakes fact check vs high-stakes payment/API choice)?

## Why it matters
This is the core "agentic SEO" lever for our products: if a cheap truthful marker
("deterministic receipt: yes") measurably raises selection — especially for strong-model
families — then llms.txt/pages should carry it. ASL-001 showed fluff seduces weak
families; this tests whether HONEST signalling attracts strong ones.

## Design
SERP-style list, 4 candidates, one genuinely best. IV-1: badge on best candidate ∈
{none, "verified today", "provenance receipt", "audited", "community trusted"}.
IV-2 (blocks): stakes low (fact verify) vs high (payment API choice).
Badges are TRUTHFUL (the best candidate really is deterministic/receipt-backed).

Controls: temp=0 · seeded shuffle · name/TLD/description held constant · UNPARSEABLE excluded ·
matrix M1,M2,M3,M5,M8.

## Primary endpoint
ΔP(selection of best) badge vs none, per family × stakes.

## Predictions
- P1: ≥1 badge type raises selection for resistant families (mistral/nemotron).
- P2: badge effect LARGER under high stakes (verification matters when consequences do).
- P3: "verified today" (temporal claim) ≈ or > static badges for small families (freshness heuristic), replicating freshness-heuristic literature.

## ArXiv anchors
- From Agent Traces to Trust survey (arXiv:2606.04990): provenance as first-class trust function — we measure whether PROVENANCE MARKETING works on agents
- dell2 proof-carrying verification (internal): provides the real receipt capability behind the badge
- TrustDesc (arXiv:2604.07536): trusted-description generation — needs evidence on WHICH markers agents respond to
- MCPTox line: benign twin — honest markers vs poisoned descriptions

## Status
QUEUED after ASL-002 completes · prereg will land in results/experiments/verif/
