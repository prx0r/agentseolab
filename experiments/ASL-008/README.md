# ASL-008: Structural Discovery Full Funnel

## Hypothesis
Structural web elements (JSON-LD, OpenAPI, llms.txt, sitemap presence) affect DISCOVERY but their effect must be measured through the FULL funnel (discovered→opened→selected→invoked→succeeded), not just discovery alone.

## Independent Variable
Presence/absence of structural elements, ONE at a time:
HTML title · meta description · JSON-LD schema · OpenAPI spec · MCP metadata · llms.txt · sitemap.xml · visible body copy

## Controls
Same underlying capability deployed at different URLs with different structural representations. Same search-capable agent harness.

## Primary Endpoint
Full funnel: retrieved? → ranked? → opened? → cited? → selected? → invoked? → TASK_VERIFIED?

## ⚠️ Critical Warning
SAGEO Arena (arXiv:2602.12187) found that optimizing one stage can HURT other stages. Citation-focused optimization degraded retrieval/reranking. Must measure all stages independently.

## Status
NOT YET RUN — requires deployed test pages + search-capable agent harness + real search engine access
