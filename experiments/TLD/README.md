# TLD — Does the domain extension change which result an agent picks?

## Causal Question
Holding title, description, and path IDENTICAL, does the TLD (.com / .dev / .org / .io /
.xyz) change agent selection? And does that preference interact with TASK TYPE
(technical lookup vs commercial vs factual)?

## Why it matters
FinalBuilds deploys on .workers.dev, .pages.dev, tinytools.xyz, and buys .xyz/.com at
LEVEL 2+. If agents systematically discount certain TLDs, our deployment tier choice is
a selection variable — not just a branding one. NO prior art found: trust-signal studies
(SE Ranking 2026) cover HTTPS/domain-age/schema for CONTENT pages but never TLD × task
for agentic selection. This is an open lane.

## Design
SERP-style candidate list, 5 results, identical titles+descriptions+paths except TLD.
IV-1: which TLD carries the genuinely-best result (counterbalanced across trials).
IV-2 (between-task blocks): task family — code_fix / price_lookup / fact_verify.

Controls: temp=0 · seeded position shuffle · fresh session per trial · same snippet text ·
UNPARSEABLE excluded · canonical model matrix M1,M2,M3,M5,M8 (+M9 quota permitting).

## Primary endpoint
P(selected TLD) per task family; interaction = difference-in-differences of .dev-vs-.com
preference between technical and commercial tasks.

## Predictions (preregistered)
- P1: agents show measurable TLD hierarchy rather than uniform choice.
- P2: .dev/.io premium on technical tasks; .com premium on commercial tasks (interaction).
- P3: .xyz discounted across tasks (spam association in training data).

## ArXiv anchors
- SAGE (Google 2026): agents pull from top-3 → whatever biases top-3 choice matters doubly
- Endorsement Vulnerability (arXiv:2606.16821): search-agent trust is manipulable by surface features
- SE Ranking 2026 trust-signal analysis (content pages): domain signals carry weight — we test whether TLD alone carries any for AGENT selection
- Agentic Search in the Wild (ACM IR 2026): real query trajectories show surface-form sensitivity

## Status
RUNNING 2026-08-23 · prereg: results/experiments/tld/PREREG_*.json
