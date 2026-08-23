# AgentSEOLab — Execution Grounding Sprint
**2026-08-23 · FREEZE all stated-preference experiments until this sprint completes**

## Prime Directive (replaces all prior)

> No agent-behavior claim may be based primarily on what an agent says it would do.
> A behavioral claim requires an observable environment action.
> A performance claim requires a verifier external to the agent.
>
> **Agent statements are telemetry, never ground truth.**

## Construct validity assessment

| Area | Status |
|------|--------|
| Provenance / immutable records | Strong |
| Self-invalidation / scientific honesty | Strong |
| Position/name controls | Good |
| Cross-model testing | Good idea, weak interpretation |
| Statistical plumbing | Improved substantially |
| Trace capture | Promising |
| Construct validity | **Poor** |
| Definition of task success | **Currently invalid** |
| Execution-grounded evaluation | **Missing** |
| Generalization across tasks | **Missing** |
| Causal claims | Not ready |

## P0: invalidate contaminated evidence

1. Rename all pairwise results to STATED_SELECTION — they measure what the model SAYS, not what it DOES
2. Remove them from agent-behavior claims
3. Invalidate historical task_success computed from URL presence → rename FINAL_URL_REPORTED
4. Fix search/citation event semantics:
   - URL in tool output ≠ SOURCE_CITED
   - search engine URL opened ≠ SEARCH_RESULT_EXPOSED (CAPTCHA-blocked ≠ exposed)
   - agent mentioned URL ≠ CAPABILITY_SELECTED
   - capability selected ≠ invoked
   - tool returned 200 ≠ task succeeded

## L0 demoted to hypothesis generation

L0 = Preference probe. Measures P(textual_selection | description, task, model).
Allowed conclusion: "Under forced-choice prompt, model X selected A 82% of the time."
Forbidden conclusion: "Agents prefer tools with property A."
Does NOT enter main evidence ledger as agent behavior.

## Build four real levels

L1 Simulated invocation: actual function defs, observe CAPABILITY_INVOKED
L2 Stateful sandbox: real behavior per tool, state transitions, deterministic verifier
L3 Controlled browser/search field run
L4 Real deployed capability + outcome

Primary endpoint for almost every experiment: TASK_VERIFIED ∈ {0,1}
Self-report goes at the bottom of the measurement hierarchy.

## The intention–action gap experiment

Measure P(stated_selection=X) vs P(first_invocation=X) vs P(success | first_invocation=X)
across models/tasks/tool-set sizes/capability quality levels.
If the gap is large enough to be interesting → first genuinely great result.

## Experimental unit fix

Independent unit = task × initial_state × treatment_assignment
NOT individual model call.
Repeated calls on one task estimate stochasticity, not task population.

Replication hierarchy:
Internal (same tasks, new seeds) < Cross-model < Cross-task < Cross-domain < Cross-scaffold < External/field

REPLICATED = directional effect survives independently frozen task suite + another model family or environment.

## Factorial design over atomic features

Evidence provenance 0/1 · Freshness timestamp 0/1 · Outcome guarantee 0/1 ·
Quantitative specificity 0/1 · Credential disclosure 0/1 · Failure disclosure 0/1 ·
Structured parameters 0/1 · Tool name semanticity

Estimate main effects AND interactions. Current stimuli change 8 things simultaneously.

## Model-vs-harness confound

"Model scale determines strategy" is premature — simultaneously varying:
model/provider/system prompt/tool serialization/sampling/reasoning/API wrapper/scaffold.
Call it "observed model-condition association" until crossed with scaffold.

## Reliability metrics

pass@1 (capability-ish) + pass^k (reliability). A treatment that changes success 72→78%
but reduces consistency may be WORSE in an agent economy.

Add perturbation tests (metamorphic task variants must preserve effects).
Add fault injection (timeout, 429, 500, malformed JSON, stale, credential failure...).

## Statistics upgrade path

Single fixed task: Wilson/binomial is fine, report as within-task execution probability.
Task suite: aggregate at TASK level, paired bootstrap over tasks.
Eventually: mixed-effects logistic regression with task random intercepts.
Stop using n≥30 as magic threshold. Use pilot → power calculation → preregistered confirmatory run.

## Database separation

Episode (one autonomous attempt) / Action / StateTransition / Evaluation
Agent utterance = another observation inside Episode, no privileged status.

## Unique scientific question

What machine-readable signals causally change autonomous-agent discovery, invocation and successful execution?
Funnel: DISCOVERED → EXPOSED → INSPECTED → SELECTED → INVOKED → EXECUTED → VERIFIED → REUSED
Mutate: name/description/schema/examples/provenance/freshness/price/latency/reliability/
permissions/verification/reputation/failure disclosure at every stage.

## First great paper target
"Agents don't use what they say they would use"
Same candidates in Survey condition vs Behavior condition.
Compare stated preference vs actual invocation vs verified task outcome across models/tasks/tool-set sizes.

---

# Execution order

P0: Invalidate bad semantics (rename + reclassify existing data)
P1: Build one tiny executable world (4 MCP tools, 1 task family, hidden verifier, resettable env)
P2: Prove pipeline (10 tasks × 2 conditions × 3 models × 3 rollouts, record actual calls only)
P3: ASL-001 rigorous (intention–action gap measurement)
P4: Description causal test (one feature, randomized paired, TASK_VERIFIED primary endpoint)
P5: Held-out replication (new tasks, different model family, frozen spec)

Do NOT start evolution, ASL-002–008, or large sweeps before P5 completes.
