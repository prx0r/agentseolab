# Frontier research translated into design requirements

This document records the research ideas the infrastructure is designed around.

## Search-Augmented GEO must be end-to-end

SAGEO Arena (Kim et al., 2026) argues that evaluation on a predetermined candidate set omits retrieval and reranking and can mis-estimate real visibility. It also reports that optimization strategies can degrade earlier pipeline stages and that structural web information matters.

Design implication:
- keep controlled candidate experiments, but never equate them with field visibility;
- explicitly measure retrieval -> reranking -> generation/citation stages;
- preserve structural page variants.

Reference: https://arxiv.org/abs/2602.12187

## Agent discovery should use execution/behavior signals

AgentSearchBench (Wu et al., 2026) studies nearly 10,000 agents and reports a gap between semantic-description similarity and execution-grounded performance; behavioral/execution-aware probing improves ranking.

Design implication:
- domain/agent discovery scores should incorporate actual downstream success;
- "description sounds relevant" is not sufficient;
- retain invocation/task-success outcomes.

Reference: https://arxiv.org/abs/2604.22436

## LLM judges have position bias

Shi et al. (2024) systematically evaluate position bias across 12 LLM judges and more than 100k evaluation instances.

Design implication:
- randomize order;
- perform swapped-order repeats;
- measure position consistency;
- fit preference models from raw pairwise outcomes rather than trusting one judge response.

Reference: https://arxiv.org/abs/2406.07791

## AI search engines differ and queries matter

Chen et al. (2025) report engine-specific differences in sourcing, freshness, domain diversity, language behavior and query-phrasing sensitivity.

Design implication:
- stratify by engine/model/version/language;
- retain raw query formulations;
- never publish one universal score without breakdowns.

Reference: https://arxiv.org/abs/2509.08919

## Retrieval tasks can require reasoning beyond lexical similarity

BRIGHT (Su et al., 2024) constructs realistic reasoning-intensive retrieval tasks and hard negatives, illustrating why semantic/lexical overlap alone is insufficient.

Design implication:
- use realistic task intents and hard-negative candidate domains/pages;
- evaluate task usefulness, not only textual similarity.

Reference: https://arxiv.org/abs/2407.12883
