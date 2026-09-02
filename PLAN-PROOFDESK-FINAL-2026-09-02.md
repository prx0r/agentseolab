# ProofDesk — Final Win-Probability Dev Plan

## Current verdict

ProofDesk is now technically in the strongest state of the three submissions.

Latest commit audited: `2f29387bcde861ebed57231fa408cc16d60c2739`.

The important change is that **GitHub Actions is now green** on the latest push. The four canonical PDFs are committed, the clean-clone fixture failure is fixed, the Merkle bug was fixed, hard-coded API keys were removed from tests, and the README/docs were rewritten Nutrient-first.

This means ProofDesk is no longer primarily a coding problem. It is now a **presentation + sponsor-proof + research-proof problem**.

The submission should be optimized around one memorable sentence:

> **Both document values were extracted correctly with high confidence. Together, they describe an unsafe transaction — so ProofDesk refuses to act.**

That is the magic trick.

---

# P0 — Website reliability before recording

The deployed page source currently points its frontend to an ephemeral TryCloudflare backend URL:

`https://commons-orange-reporters-reproduce.trycloudflare.com`

That is not reliable enough for judging.

## Fix

Use one of:

1. a stable Cloudflare Worker/Pages Function proxy to the ProofDesk API,
2. a stable VPS hostname,
3. a durable tunnel hostname you control.

The public page should never depend on a temporary `trycloudflare.com` tunnel that may disappear after the recording.

Acceptance:

- reload public page from another device/private tab
- click `run live`
- full procurement flow succeeds
- repeat 3 times
- backend survives browser refresh
- CORS works
- no credentials exposed to the browser

---

# P0 — Make Nutrient visibly undeniable

The current live procurement page says `nutrient dws` in the UI and shows extracted facts, but the frontend does **not currently make the sponsor call itself visible enough**.

At the moment the live path calls:

- `/v1/cases/fixture`
- `/run`
- `/facts`
- `/assertions`
- `/signature-gate`
- `/events`

That proves the ProofDesk product, but a Nutrient judge should be able to see in one glance:

> **NUTRIENT DWS — LIVE — 200 — 842 ms**

and then the exact fields it produced.

## Add a provider proof strip to the top of the live result

Call `/v1/providers/status` before the run and render something like:

```text
Nutrient DWS       LIVE
Extraction mode    LIVE
Source grounding   ENABLED
```

Then call `/v1/cases/{id}/trace` and render a compact sanitized trace:

```text
NUTRIENT DWS
POST extraction/build-or-extract
200
842ms
insurance_certificate.pdf
```

Do not expose authentication headers.

The sponsor proof should appear **before** the long ProofDesk audit logic.

## Important truth rule

If Nutrient is unavailable or the backend is running replay/stub mode:

```text
NUTRIENT DWS — REPLAY
captured real DWS response
```

Never allow the page to say LIVE when the provider is stubbed.

---

# P0 — Surface page/bounding-box provenance

The product already exposes page and bbox grounding. The website currently mostly displays confidence + page.

That leaves sponsor value on the table.

For the two hero facts in the contradiction, show:

```text
procurement.required_coverage
2027-10-01
confidence 0.98
page 1
bbox [x1,y1,x2,y2]
[Nutrient source]

insurance.expiry_date
2027-08-31
confidence 0.97
page 1
bbox [x1,y1,x2,y2]
[Nutrient source]
```

Best version: clicking `source evidence` opens a small document preview with the source rectangle highlighted.

If building a PDF preview costs too much time, the compact page+bbox+filename display is enough.

The point is to make visible:

> this is not an LLM opinion; this value is grounded in a location in the source PDF.

---

# P0 — Complete the visible ending

The current website resolution flow is good:

1. blocker
2. human conditional accept
3. approve
4. generate
5. re-run gate

But after the gate passes, the page does not yet give the judge a sufficiently strong **final object**.

Add a final `VERIFIED DECISION RECEIPT` panel.

Show:

```text
case_id
human actor
resolution reason
record hash
artifact hash
decision certificate hash
audit root
gate: PASS
```

And visually end the main flow on:

```text
AUTHORIZED
artifact integrity verified
```

This should be the final screen in the video.

The judge needs a visible state transition:

```text
BLOCKED
    ↓ human judgment
AUTHORIZED
```

---

# P0 — Archive/replace the stale demo script

`docs/DEMO_SCRIPT_FINAL.md` is currently dangerous because it describes a different presentation:

- 18 PDFs
- 45 fields
- 9 document types
- DWS Viewer flow
- VerifyDoc comparison
- Foxit merge

Do **not** use that script for the current Nutrient submission.

Archive it or replace it with one canonical `DEMO.md`/`DEMO_SCRIPT_FINAL.md` matching the deployed website exactly.

There must be one authoritative script tomorrow morning.

---

# The exact demo I would record

Target: **2:50–3:15**.

Do not begin with architecture or research.

## 0:00–0:13 — Hook

Screen: ProofDesk live page before clicking Run.

Say:

> “Document AI usually asks one question: did I extract the field correctly? But an individually correct fact can still be unsafe to act on. ProofDesk separates evidence from authority.”

## 0:13–0:30 — Run live Nutrient

Click `run live`.

As provider status/trace appears:

> “These four procurement PDFs are being processed through Nutrient DWS. Nutrient is the evidence layer: it extracts structured fields with confidence and source provenance.”

Pause on the LIVE Nutrient trace.

## 0:30–0:58 — The contradiction

When the two hero facts appear side-by-side:

> “Here’s the failure we care about. The procurement request needs insurance through October first. The certificate expires August thirty-first. Both values were extracted correctly and with high confidence — but together they describe a thirty-one-day uninsured gap.”

Then:

> “A normal extraction pipeline can call this a success. ProofDesk calls it unsafe.”

This is the strongest line in the video.

## 0:58–1:22 — Authority gate

Scroll to the deterministic assertions and gate.

> “ProofDesk reconciles facts across documents with deterministic checks. The agent cannot negotiate with the gate. An unresolved blocker and missing human approval mean execution is denied.”

Pause on:

`BLOCKED — agent cannot sign`

## 1:22–1:47 — Human judgment

Click resolve.

> “Instead of sending a person the entire document bundle, ProofDesk routes the exact disputed assertion and its evidence. The reviewer records a decision, actor and reason. Human judgment becomes part of the evidence trail.”

Use the existing conditional acceptance reason.

## 1:47–2:13 — Authorized artifact

After approve/generate:

> “The system re-evaluates the same gate. Now the exception is resolved, human authority is present, and the generated artifact is cryptographically bound to the approved record.”

Show PASS + receipt hashes.

> “Change the approved bytes afterwards and the hash no longer matches.”

If the tamper button is rock-solid, click it here for 5–8 seconds. Otherwise leave tamper for the website/research section.

## 2:13–2:35 — Audit

Show hash-chained events/receipt.

> “Every state transition is recorded, so the final authorization can be replayed from the evidence instead of trusting a black-box AI decision.”

## 2:35–2:55 — Extra-credit research

Open the future `Trust Lab` section/tab.

> “We also treated this as a reliability research problem. We benchmark when document confidence is actually safe enough for automation, how review thresholds trade automation against false authorization, and how human corrections recalibrate the policy over time.”

Show one strong real graph, not six.

## 2:55–3:08 — Close

Return to final authorized receipt.

> “Nutrient gives agents grounded document evidence. ProofDesk decides when that evidence is strong enough to act — and when a human must take control.”

End on the verified receipt, not a thank-you slide.

---

# Extra credit — build a real Trust Lab on the website

This is the major missing piece from the current public page.

Right now the page has:

- live procurement
- static insurance scenario
- static contract scenario
- static trade scenario
- beyond-procurement table

That is good product breadth, but it does **not yet surface the huge research program**.

Add a fifth top-level tab or a section below the live demo:

> **Trust Lab / AuthorityBench**

Do not mix this into the main flow before the judge understands the product.

## Minimum viable research surface

Three real charts generated from committed benchmark JSON:

### 1. Risk–coverage frontier

X: fraction of cases automatically authorized

Y: false authorization rate among auto-authorized cases

Compare whatever you can genuinely measure, e.g.:

- raw confidence threshold
- calibrated confidence
- + cross-document assertions
- full ProofDesk gate

This is the hero research graph.

### 2. Reliability diagram

Predicted confidence vs observed correctness.

If you have enough actual Nutrient labeled examples, show raw vs calibrated.

If not, do not invent it. Use existing validated research results and label the source dataset clearly.

### 3. Learning from review

Sequential replay:

X: human reviews accumulated

Y1: review rate

Y2: audited automated error

This makes the online calibration work visible.

Optional fourth visual:

### 4. Deterministic integrity experiment

Take approved artifacts and mutate one byte / text field.

Report actual test result:

```text
N mutated artifacts
N detected
```

This is a very easy, defensible wow result.

---

# AuthorityBench — what to actually implement now

`docs/AUTHORITYBENCH_PLAN.md` exists and is extensive. Do not try to implement every idea before submission.

Build `AuthorityBench v0.1` around the canonical procurement fixture only.

Generate controlled cases such as:

- safe bundle
- insurance date mismatch
- quote total mismatch
- missing insurance certificate
- conflicting vendor identity
- expired security questionnaire
- near-threshold confidence

Each case should have:

```json
{
  "case_id": "...",
  "ground_truth_authority": "ALLOW|REVIEW|BLOCK",
  "facts": [...],
  "assertions": [...],
  "policy_result": "..."
}
```

Then replay your current policy over them.

The contribution is not “best OCR.”

It is:

> **Does the system prevent unsafe downstream authority even when extraction itself looks successful?**

That is a much more original benchmark question.

---

# Research hygiene

The old Foxit research is useful, but it should be presented as the lab that informed ProofDesk, not as part of the Nutrient product.

Keep the `foxit/README.md` banner strong:

> historical research laboratory; canonical product is `/src`; current submission is Nutrient DWS.

Do not headline old credit-card fraud benchmarks in the demo.

Do not use simulated graphs from historical presentation scripts as scientific results.

Do not claim formal conformal/CRC guarantees unless the current implementation satisfies the stated finite-sample procedure.

Use language such as:

- “risk-calibrated”
- “conformal-inspired / evaluated with risk-coverage methods”
- “empirically controlled on this benchmark”

rather than universal safety guarantees.

Every research graph should be generated from a committed result artifact.

---

# Technical preprint

If AuthorityBench v0.1 yields real enough results, make a 5–8 page PDF in the repo:

**From Confidence to Authority: Evidence-Gated Document Automation with Source-Grounded Extraction**

Sections:

1. Introduction
2. Extraction confidence vs execution authority
3. ProofDesk architecture
4. AuthorityBench protocol
5. Nutrient DWS evidence
6. Risk/coverage evaluation
7. Human review and online calibration
8. Integrity/audit layer
9. Limitations
10. Conclusion

Call it `technical preprint`, not “arXiv paper,” unless actually submitted.

The public site should have a small row:

`[GitHub] [Technical Preprint] [Benchmark Results]`

This is for the technical judge after the product wow moment.

---

# Website changes — exact priority

## Must have

- stable backend hostname
- `Nutrient DWS LIVE` provider status
- actual sanitized Nutrient provider trace
- source filename/page/bbox for the two hero facts
- final decision receipt + hashes after resolution
- accurate LIVE vs REPLAY labeling
- no stale Foxit/Doctavian references on primary path

## Strong extra credit

- Trust Lab tab
- one risk/coverage chart
- one calibration/learning chart
- technical-preprint link
- tamper experiment

## Nice, not necessary

- PDF source preview with highlighted bbox
- additional industry scenarios becoming fully interactive

The current insurance/contract/trade examples are fine as static breadth if they say **PRECOMPUTED SCENARIO** prominently.

---

# Repo cleanup before final submission

The repo is now green, but the judge-facing root still has a lot of historical material.

Keep root minimal:

```text
README.md
HACKATHON_SUBMISSION.md
LICENSE
STATE_MACHINE.yaml
src/
site/
fixtures/
tests/
benchmarks/
docs/
foxit/   # clearly historical research lab
```

Historical Doctavian docs currently still exist under `docs/`. They should either move to `docs/archive/` or have an unmistakable historical banner. A judge should not accidentally open `DOCTAVIAN_INTEGRATION_SPEC.md` and wonder what the actual submission is.

README top should have:

```text
[Live Demo] [2–4 min Video] [Judge Guide] [Research / Trust Lab]
```

once available.

---

# Final acceptance checklist

- [ ] latest CI green
- [ ] public page stable for 3 repeated runs
- [ ] backend is not temporary TryCloudflare
- [ ] provider status visibly says Nutrient LIVE during recording
- [ ] real Nutrient trace visible
- [ ] page/bbox provenance visible
- [ ] contradiction is deterministic every run
- [ ] gate visibly blocks
- [ ] resolution captures actor + reason
- [ ] final gate passes
- [ ] receipt/hash visible
- [ ] live/replay/precomputed states never conflated
- [ ] research section uses real benchmark artifacts only
- [ ] stale demo script archived/replaced
- [ ] historical Doctavian/Foxit docs cannot confuse judges
- [ ] Devpost repeats exact DWS-heavy-lifting sentence

## DWS heavy-lifting sentence

> **Nutrient DWS performs the core document extraction and source grounding that turns uploaded PDFs into confidence-aware evidence; ProofDesk uses that evidence to determine whether an automated action may proceed or must defer to a human.**

## Final positioning

Do not sell “AI procurement.”

Sell:

> **ProofDesk is an authority layer above document intelligence: evidence → policy → human judgment → irreversible action.**

That generalizes immediately to procurement, AP, insurance, lending and compliance.

The product is already strong enough. The remaining probability gain comes from making the live Nutrient proof, authority transition and research depth impossible for a judge to miss.
