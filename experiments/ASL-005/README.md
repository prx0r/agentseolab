# ASL-005: Parameter Schema Fitness

## Hypothesis
Parameter schema clarity (names, required fields, examples, complexity) affects valid invocation rate independently of description quality and tool selection accuracy.

## Independent Variable
Schema design: clear names+examples / ambiguous names / excessive required args / nested oneOf / enum without descriptions

## Controls
Same tool functionality. Same description. Only inputSchema differs.

## Primary Endpoint
parameter_valid_rate — fraction of invocations with correctly constructed arguments

## ArXiv References
- MCP-RADAR (arXiv:2505.16700) — multi-dimensional tool use benchmark measuring selection AND parameter construction separately
- MCPAgentBench (arXiv:2512.24565) — distractor-rich MCP environments
- MCPToolBench++ (arXiv:2508.07575) — AST evaluation of structural correctness

## Status
NOT YET RUN — requires MCP sandbox
