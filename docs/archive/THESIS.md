# UPDATED THESIS — AgentSEOLab in the unified system (2026-08-23)

## Identity
AgentSEOLab is an **empirical laboratory** studying how autonomous agents discover,
evaluate, select, invoke, trust and reuse machine-readable capabilities. It is NOT an
SEO product. It is **FinalBuilds' external behavioural laboratory**: it measures the
ecology in which every FinalBuilds product must survive.

## The two-way contract with FinalBuilds / Hydra

### 1. FinalBuilds asks → AgentSEOLab tests causally
FinalBuilds never relies on aggregate traffic alone. Hypotheses like
*H2: machine-discoverable agent-native tools achieve greater repeated usage than
equivalent human-oriented services* are decomposed into controlled subclaims:

| Subclaim | Experiment class |
|---|---|
| Does adding MCP change invocation? | deployment-variant A/B |
| Does llms.txt change discovery? | discovery funnel |
| Does authoritative provenance change selection? | selection probe |
| Does lower latency change reuse? | repeat-use panel |
| Does machine-readable pricing change invocation? | invocation probe |
| Does deterministic verification change repeat use? | receipt/repeat design |
| Does a compelling description raise selection but hurt success? | **ASL-001 ✓ DONE** |

Every FinalBuilds app doubles as a field experiment: deploy variants A(normal docs)
→ B(machine-readable) → C(MCP) → D(MCP+provenance) → E(MCP+deterministic receipt),
then measure exposure → selection → invocation → valid invocation → task success →
repeat use → latency → cost. **The product portfolio itself becomes scientific
instrumentation.**

### 2. AgentSEOLab generates anomalies → Hydra abduces product theses
Lab observations enter Hydra as EvidenceClaims (contracts/hypotheses/
evidence-claim.v1.schema.json: claim, quantities, provenance_hash). Example chain:

```
OBS small models ignore tool descriptions          (ASL-001 v2: seduced families)
OBS large models evaluate description content      (ASL-001 v2: resistant families)
OBS all models penalise complex parameter schemas  (ASL-005, pending)
OBS verification improves reuse, barely selection  (receipt experiments, pending)
        ↓ Hydra convergence-detector + abductive generation
H17: Agent-tool adoption bottlenecks shift with model capability:
     weak agents are interface-complexity-constrained;
     strong agents are trust/reliability-constrained.
```

This is a genuinely new PRODUCT THESIS generated from measured behaviour, not opinion.
Relevant method literature: ICLR 2026 controlled abductive hypothesis generation over
knowledge graphs; HypoAgent's graph-neighbourhood probing to refine unreliable
hypothesis fragments. AgentSEOLab is the high-quality empirical feeder that keeps
Hydra's abduction from exploding into redundant speculation.

## Why this matters scientifically (frontier anchors)
- MCPTox (2026): tool-description poisoning hits 72.8% attack success; <3% of agents refuse.
  Our ASL-001 v2 result is the benign twin: marketing fluff flips selection 0%↔100% BY FAMILY
  (Qwen/Gemma/GPT-OSS-20b seduced; Mistral/NVIDIA/ox resistant).
- TrustDesc (arXiv:2604.07536) assumes one universal trusted-description style. Our family
  heterogeneity says description generators must be evaluated per agent population.
- MCP-AgentBench (AAAI 2026): outcome-oriented evaluation of operational tools, not claimed intent —
  matches our Prime Directive (agent statements are telemetry; verifiers are ground truth).
- GEO (2311.09735) → AgenticGEO (2603.20213) optimise content visibility. Nobody has built the
  equivalent for TOOL descriptions. That gap — Tool GEO — is AgentSEOLab's niche.

## Measurement ontology (never collapse)
```
DISCOVERY FUNNEL : SEARCH_RESULT_EXPOSED → OPENED → SOURCE_READ → SOURCE_USED → SOURCE_CITED
CAPABILITY FUNNEL: CAPABILITY_SELECTED → INVOKED → EXECUTION_SUCCEEDED → TASK_VERIFIED
REUSE LAYER      : repeat_use, latency, cost  (panel measurement over time)
```
One number per stage; never a single blended score.

## Evidence discipline (unchanged, non-negotiable)
Preregistration + manifest hash · temp=0 · seeded AB/BA · name↔description decoupling ·
fresh sessions · UNPARSEABLE ≠ wrong · Wilson CI per estimand · REPLICATED requires ≥2
model families agreeing · INVALIDATED records preserved forever · generator/judge separation.
