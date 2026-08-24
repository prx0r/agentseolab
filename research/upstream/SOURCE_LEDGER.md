# Source Ledger — research/upstream

Reference-only clones. Nothing here is imported into the product wholesale.

| Repo | Commit (cloned) | License | What we learned / reuse |
| --- | --- | --- | --- |
| Bingo-W/AgentSearchBench | (see git log) | MIT | Execution-grounded relevance beats description similarity; probing methodology |
| lmarena/arena-rank | " | Apache-2.0 | Bradley–Terry implementation patterns, leaderboard statistics |
| tatsu-lab/alpaca_eval | " | Apache-2.0 | Annotator abstraction, caching, randomized ordering, evaluator bias analysis |
| dorukardahan/domain-search-mcp | " | (check repo) | MCP UX, caching, availability failure handling, anti-slop baseline |
| lmarena/search-arena | " | (check repo) | Real search traces, BT analysis, intent categorization |
| lm-sys/FastChat | " | Apache-2.0 | Randomized anonymous arena battles (study only) |
| macanderson/arena | " | MIT | ABBA scheduling, held-out verification, Wilson/McNemar/bootstrap |
| faizul666/domain-search-agent | " | (check repo) | Weighted-score competitor baseline to beat experimentally |
| bitbuilder-io/domains | " | MIT | Domain-search UI components if needed |
| AIcling/agentic_geo | " | (check repo) | MAP-Elites + surrogate critic (post-MVP study) |

Fill in exact commit SHAs after each clone: `git -C <repo> rev-parse HEAD`.
