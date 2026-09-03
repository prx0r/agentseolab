# DomainArena — Recording Script (3:35)

**Open https://domainarena.tradesprior.workers.dev/ in Chrome. Full screen. Read aloud.**

---

## 0:00–0:15 — Hook

**Screen:** Hero visible. "Measure the name before you buy it."

> "Humans choose domains by intuition. But increasingly the thing discovering your service is an AI agent. DomainArena measures whether the agent understands the name before you buy it."

---

## 0:15–0:40 — Discovery

**Screen:** Click "Run Live Demo". Watch Step 1 (Product Intent) and Step 2 (name.com Discovery) appear.

> "I give DomainArena a product intent: a JSON repair API for AI agents. name.com searches for available domains matching the intent."

**Point at the search terms: "jsonrepair, fixjson, jsonvalidate"**

> "Three search terms, multiple TLDs. name.com returns live candidates with real pricing."

---

## 0:40–1:10 — Blind Agent Test

**Screen:** Watch Step 4 (Blind Agent Test) appear with scores.

> "Each domain is tested with Llama 3.3 70B — blind, no context, no description. Then an independent Mistral evaluator scores the inference against the frozen intent."

**Point at the scores. Stop on one miss and one hit.**

> "The domain that sounds coolest to a human isn't necessarily the one an agent understands."

---

## 1:10–1:30 — Recommendation

**Screen:** Step 5 (Measured Winner) shows the winner with score and pricing.

> "That becomes evidence for the purchase decision. The measured winner is selected by agent comprehension score, not human intuition."

---

## 1:30–2:00 — Fresh Recheck

**Screen:** Step 6 (Fresh Checkout Revalidation) shows AVAILABLE.

> "But we don't trust the old search result. DomainArena calls name.com again to recheck availability and price before any money moves."

---

## 2:00–2:20 — Register + DNS

**Screen:** Steps 7-8 show REGISTERED and DNS.

> "A human approves the purchase. name.com registers the domain. Then we create DNS and read it back to verify the domain is actually configured."

---

## 2:20–2:40 — Receipt

**Screen:** Step 9 shows the SHA-256 receipt.

> "The entire decision is frozen into a cryptographic receipt. Measured, approved, acquired, verified."

---

## 2:40–3:00 — Research

**Screen:** Scroll to Research section.

> "This grew out of 16 experiments across seven-plus model families. Position matters, model families disagree, and polished descriptions can seduce agents toward broken tools."

---

## 3:00–3:15 — Frontier

**Screen:** Narrate.

> "Cloudflare is measuring whether deployed sites are agent-ready. DomainArena attacks the earlier decision: before deployment, which name should the machine audience see?"

---

## 3:15–3:35 — Close

> "Measure the name. Buy the evidence-backed winner. Verify the infrastructure."

**End on the receipt showing MEASURED → APPROVED → ACQUIRED → VERIFIED.**

---

## Key Numbers

| Number | Value |
|--------|-------|
| name.com endpoints | 6 (search, checkAvailability, getPricing, register, DNS create, DNS readback) |
| Experiments | 16 across 7+ model families |
| Tests | 148 passing |
| Inference model | Llama 3.3 70B (blind) |
| Evaluator model | Mistral Small 3.1 (independent) |
| Intent | "JSON repair API for AI agents that validates and repairs malformed JSON" |

## If a Judge Asks

**"Is the full research running in the browser?"** — The browser runs a live fast path: one inference model, one independent judge, real Workers AI. The full AB/BA cross-family research runs in the committed experiment harness — that's the deeper study, not the live demo.

**"Why is the receipt real?"** — It's a SHA-256 over the entire decision chain: domain, intent hash, experiment hash, prices, registration status, DNS verification. Not random bytes. Content-addressed and independently verifiable.

**"What if the domain gets taken?"** — DomainArena re-checks with name.com before registration. If availability or price changed, it fails closed. The purchase never proceeds on stale data.
