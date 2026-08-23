# ASL-005: Parameter Schema Fitness

## Hypothesis
Parameter schema clarity (names, required fields, examples) affects valid invocation rate independently of description quality.

## Independent Variable
Parameter schema design: clear names / ambiguous names / excessive required args / missing examples / nested complexity

## Controls
Same tool functionality. Same description quality. Only inputSchema differs.

## Primary Endpoint
`parameter_valid_rate` — fraction of invocations with correctly constructed arguments

## ArXiv References
- MCP-RADAR (arXiv:2505.16700) — multi-dimensional tool use benchmark
- MCPAgentBench (arXiv:2512.24565) — distractor-rich MCP environments

## Status
NOT YET RUN — requires MCP sandbox
