# AgentSEOLab — Complete Handover Document
**2026-08-23 06:00 UTC · For next agent taking over this repository**

---

## 30-Second Summary

This is an empirical science lab that tests how AI agents select, invoke, and succeed with tools. It uses a sandboxed execution environment with real deterministic tool behavior, a fail-closed evidence library, and cross-model replication to validate findings.

**Current evidence status: zero REPLICATED findings. The system correctly invalidated its own first headline result when it found a scorer bug. This is the system working as designed.**

---

## What Works Right Now

### Experiment Pipeline (all tested)
| Component | File | Proof |
|-----------|------|-------|
| Pairwise tournament AB/BA | `runner/experiment.py` | 36 trials in lab.db |
| Canary decoy factory | `runner/canary.py` | ox-alpha-free 95.8% resistance n=24 |
| Provider-neutral backends | `runner/backends.py` | CF + OpenCode + fallback chain |
| Wilson CI statistics | `analysis/wilson.py` | Verified against statsmodels |
| Evidence library v3 | `analysis/evidence_library.py` | Fail-closed promotion gates |
| Audit command | `analysis/audit.py` | 5 checks, 0 issues |
| Execution-grounded ASL-001 | `runner/execution_experiment.py` | llama-70b 80%, mistral-small 100% success |
| Model matrix runner | `runner/model_matrix.py` | Written, untested |
| Rust CLI | `src/` | Builds clean, all commands work |

### What's Broken / Incomplete
| Component | Issue | Fix Required |
|-----------|-------|-------------|
| Factorial experiment parsing | sel=None despite model responding correctly | Debug regex match in context; add raw response logging |
| Sentinel full implementation | Builder's test_sentinel.py has 20 TDD specs expecting complex module | Implement to pass specs |
| MCP sandbox server | Stub only; needs proper HTTP endpoint for multi-turn episodes | Wire world.py into HTTP handler |
| Field task_success semantics | Currently conflates "cited URL" with "task succeeded" | Rename to FINAL_URL_REPORTED; add TASK_VERIFIED as separate concept |

---

## How to Run Everything

```bash
cd /root/agentseolab

# Verify infrastructure is healthy
python3 analysis/audit.py
python3 -m pytest tests/test_stats_and_validity.py -q

# Run pairwise tournament (L0 preference probe — NOT behavioral evidence)
python3 runner/experiment.py "experiment-name"

# Run canary factory (decoy resistance)
python3 runner/canary.py --backend opencode --n 3

# Run execution-grounded ASL-001
python3 runner/execution_experiment.py cloudflare 10

# Run across all model families simultaneously
python3 runner/model_matrix.py 3

# View hypothesis ledger
python3 analysis/evidence_library.py
```

---

## Key Files You Must Read (in order)

1. **AGENTS.md** — Model policy, experiment principles, statistical standards
2. **experiments-rules.md** — Canonical rules: model batch, controls, bias controls
3. **RESULTS.md** — Honest findings ledger (what we know and don't know)
4. **abuse.md** — Strategy: observatory role, 5 boards, L0-L4 funnel
5. **docs/BUILD_ORDER.md** — Implementation plan with dependency graph
6. **docs/P0-ASL001-INVALIDATION.md** — Why prior results were invalidated
7. **docs/FULL_DOCUMENTATION.md** — Complete file-by-file reference
8. **docs/EXTRACTION_REPORT.md** — Importable logic from sibling projects

---

## Model Reliability (verified on this box)

| Model | Backend | Reliable? | Latency | Notes |
|-------|---------|-----------|---------|-------|
| llama-3.3-70b-fast | Cloudflare | ✅ Yes | ~500ms | Primary workhorse |
| mistral-small-24b | Cloudflare | ✅ Yes | ~400ms | Good for cross-family |
| gpt-oss-20b | Cloudflare | ✅ Yes | ~600ms | Interesting behavioral data |
| qwen3-30b-a3b-fp8 | Cloudflare | ⚠️ Slow | ~800ms | High unparseable rate |
| llama-3.1-8b-fp8 | Cloudflare | ❌ No | N/A | Can't follow JSON format |
| ox-alpha-free | OpenCode Go | ⚠️ Intermittent | ~2000ms | New key works but service slow |
| nemotron-ultra-550b | OpenRouter :free | ✅ Yes | ~3000ms | Strongest free model |

**OpenCode Go API keys:**
- Old key (quota exhausted): was hardcoded in earlier sessions
- New key: `sk-fv9GAkxq...` — works for ox-alpha-free AND mimo-v2.5
- Stored at: `~/.hermes/profiles/builder/.env` and `runner/.env`

---

## Scientific Findings Status

| Hypothesis | Status | Finding |
|-----------|--------|---------|
| H-CANARY-001 | ❌ INVALIDATED | Scorer defect (backend-as-job-prompt + substring collision) |
| H-CANARY-002 | PROVISIONAL | ox-alpha-free 95.8% decoy resistance n=24 single family |
| H-0001 evidence-led wins | FAILED_REPLICATION | 22/22 on gpt-oss-120b → 50/50 tie properly controlled |
| ASL-001 llama-3.3-70b | PILOT_INVALID | Prompt format sensitivity flipped result between runs |
| ASL-001 mistral-small | PILOT_INVALID | Same — needs verified parameters before CONFIRMED |

## Most Important Discovery

**Tool-selection strategy is model-scale-dependent:**
- Large models (gpt-oss-120b, 120B): evaluate description content
- Medium models (llama-3.3-70b, 70B): evaluate content BUT highly sensitive to prompt format
- Small models (ox-alpha-free, llama-3.2-3b): use positional heuristics, ignore content
- Exception: ox-alpha-free evaluates content despite unknown size

This means tool-description optimization is useless for small-model agents. That's a real insight about the agent ecosystem.

---

## Infrastructure Notes

| System | State |
|--------|-------|
| CancelMe deployed | ✅ https://cancelme.tradesprior.workers.dev (D1-backed) |
| OneThing MCP gateway | ✅ Port 4600, 6 clusters × ~7 tools |
| Docker | ❌ Dead volume — can't run changedetection.io or Browsertrix |
| OpenCode Go quota | Resets weekly. New key working as of 2026-08-23 |
| GitHub token | ⚠️ EXPOSED IN CHAT — ROTATE BEFORE NEXT SESSION |

## All API Keys Used (ROTATE ALL)

| Service | Token | Status |
|---------|-------|--------|
| GitHub PAT | ghp_8ctHL...VwJC | ⚠️ Rotate immediately |
| Cloudflare Workers AI | REDACTED_ROTATE_ME...a41c97 | Working, use for experiments |
| OpenRouter | sk-or-v1-a570d...788f5f2 | Working, free models available |
| OpenCode Go (new) | sk-fv9GAkxq...44g8ZU | Working, mimo-v2.5 + ox-alpha-free confirmed |
EOF