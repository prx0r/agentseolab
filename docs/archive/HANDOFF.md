# Integration handoff for domainnamechecker

## P0
1. Replace DNS-derived "availability" with authoritative multi-stage verification.
2. Keep DNS as an evidence source only.
3. Add an append-only experiment/event database using the schemas in this package.
4. Add immutable SiteIntent capture before candidate generation.
5. Implement field search-trace ingestion.
6. Implement controlled hostname pairwise experiments with identical snippets.
7. Separate generator and judge sessions/providers.
8. Randomize/swap candidate ordering.
9. Add candidate lineage and challenger rounds.
10. Add pairwise human feedback.

## P1
11. Add registrar adapters and total-cost projections.
12. Add Bradley-Terry projections with bootstrap uncertainty.
13. Add query clustering while retaining raw queries.
14. Add model/version/time stratified dashboards.
15. Add held-out intent evaluation.
16. Add evidence-library hypothesis objects.
17. Link winning domain + immutable original intent into AgentSEO.

## P2
18. Run controlled experiments over title, description, path, schema, OpenAPI and MCP descriptions.
19. Track deployed-site retrieval/open/citation/invocation outcomes.
20. Detect model-version drift and automatically re-run sentinel experiments.

## Critical invariant

Never claim a capability merely because documentation says it exists. Probe it. The current repo's documentation/optimization report advertises MCP capabilities that are not fully implemented by the Worker/CLI; convert that lesson into a general `claimed_vs_verified` audit primitive.
