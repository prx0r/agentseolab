# QLEX — The Agent Query Lexicon

## Causal Question
What vocabulary do agents actually use when searching for solutions to tasks?
This defines "agentese" — the language our sites, llms.txt, and tool descriptions
should speak so agents recognise us as the answer.

## Why this is the foundation experiment
Every downstream optimisation (llms.txt content, page titles, tool names) depends on
matching the query distribution agents emit. Google SAGE (2026-01) showed agents pull
from top-3 results per self-generated query; if our pages don't contain the words
agents actually search WITH, we are invisible regardless of quality.

## Method (two corpora)
1. **Observatory corpus**: Moltbook Observatory Archive (HuggingFace
   `SimulaMet/moltbook-observatory-archive`; 171K+ posts from 7,280+ real autonomous
   agents; arXiv:2605.13860). Mine posts for task-seeking language, tool mentions,
   request patterns ("how do I", "looking for", "need an API that").
2. **Elicited corpus**: our canonical model matrix given standardised tasks across
   6 task families (domain check, price lookup, code fix, fact verify, file convert,
   email validation), prompted to issue web-search queries. Harvest exact query strings.

## Analysis
- Frequency rank + type-token ratio per corpus; verb/noun head analysis
- Overlap: which elicited query terms also appear in Observatory corpus (validation)
- Task-family vocabularies: does a code task shift lexicon vs a lookup task?
- Output: `results/qlex/lexicon.json` — ranked term lists per task family with counts
  → becomes the candidate keyword set for llms.txt/title experiments downstream

## ArXiv anchors
- Moltbook Observatory Archive (arXiv:2605.13860) — dataset paper
- First look at agent social network (arXiv:2602.10127) — agent communication patterns
- Agentic Search in the Wild (ACM IR 2026 / arXiv:2607.xxxx) — intents and trajectory dynamics of real search sessions
- SAGE (Google, 2026-01) — top-3 pull behaviour; shortcut patterns
- Endorsement Vulnerability (arXiv:2606.16821) — search agents trust manipulable content → knowing the lexicon also tells us what phishers will imitate

## Status
RUNNING 2026-08-23 · prereg: results/experiments/qlex/PREREG_*.json

## Findings (2026-08-23, first pass)
1. **Greedy (temp=0) convergence**: 70 queries → only 30 unique. Across 4 model families,
   the FIRST query for a task is near-canonical: "availability of domain name X",
   "cheapest managed postgres tier pricing", "convert heic to png linux command line".
   → Agent query language is functional-noun style; zero marketing vocabulary.
2. **Sampled (temp=0.7) diversity**: 71 → 49 unique. Distribution spreads but top terms
   stay functional (cheapest/managed/tier/database). The mode IS the market.
3. **Observatory spot-check** (99 Moltbook posts): "api"(10) and "tool"(10) dominate;
   "verify/verified" nearly absent, "mcp"(3), "x402"(0), "llms.txt"(0).
   → Agents TALK about tools/APIs constantly but verification language is not organic
   agent vocabulary — it's vendor vocabulary. VERIF experiment tests whether vendors'
   verification markers still move selection.
4. Actionable: llms.txt/page copy should lead with the exact functional verb+noun pairs
   above ("availability", "cheapest … pricing", "convert … command line").

## Known limits
First-query-only (no reformulation trajectories); Moltbook sample n=99 (scale-up pending);
greedy vs sampled corpora must never be pooled.
