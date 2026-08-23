# ASL-008: Structural Discovery Full Funnel

## Hypothesis
Structural web elements (JSON-LD, OpenAPI, llms.txt, sitemap presence) affect DISCOVERY stage but their effect must be measured through the FULL funnel (discovered→opened→selected→invoked→succeeded), not just discovery alone.

## Independent Variable
Presence/absence of structural elements, one at a time:
HTML title · meta description · JSON-LD · OpenAPI spec · MCP metadata · llms.txt · sitemap · visible body copy

## Controls
Same underlying capability. Only structural representation differs.

## Primary Endpoint
Full funnel: `retrieved? → ranked? → opened? → cited? → selected? → invoked? → TASK_VERIFIED?`

## Warning
SAGEO Arena found that optimizing one stage can HURT other stages. Must measure all stages independently.

## Status
NOT YET RUN — requires deployed test pages + search-capable agent harness
