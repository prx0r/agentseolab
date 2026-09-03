# DomainArena — Presentation Script (2:30 minutes)

---

## The Problem (0:00 — 0:20)

> "Domain names were designed for humans. But increasingly the thing discovering your service is an AI agent. Nobody tells you whether the agent actually understands your domain.
>
> A human sees 'jsonrepair.dev' and thinks 'obviously a JSON tool.' An agent sees the same name and might think 'repair shop' or 'JSON documentation' or 'nothing useful.' The name that sounds best to humans isn't necessarily the one agents understand."

**Show:** Hero text on landing page. The hook: "Measure the name before you buy it."

---

## The Thesis (0:20 — 0:35)

> "DomainArena A/B tests domain names against AI agents. We freeze your product intent, search name.com for available candidates, then blind-test each domain against Llama 3.3 70B — no context, no description, just the name. An independent Mistral evaluator scores whether the agent inferred the right product.
>
> The measured winner isn't the human favorite. It's the agent-tested winner. Then we buy it through name.com, configure DNS, and verify it works."

**Show:** The pipeline on the landing page. Emphasize the blind test step and the independent judge.

---

## The Demo (0:35 — 1:20)

> "Watch."

Click **Try the Live Demo** → lands on `/demo` → click **Run Demo**.

Logs stream live:
- "Product intent frozen: JSON repair API for AI agents"
- "name.com search: jsonrepair, fixjson, jsonvalidate across .com, .dev, .ai"
- "8 candidates returned with live pricing"
- "Blind test: Llama 3.3 70B infers from domain name alone"
- "Independent judge: Mistral Small 3.1 scores inference vs intent"
- "Winner: jsonrepair.dev — agent comprehension score 0.87"
- "Fresh recheck: AVAILABLE at $12.99/year"
- "Registered via name.com API"
- "DNS configured: TXT record created and verified"
- "SHA-256 receipt: MEASURED → APPROVED → ACQUIRED → CONFIGURED → VERIFIED"

> "The domain that scored highest with agents wasn't the one humans preferred. jsonrepair.dev scored 0.87 with agents. The human-favorite jsonfix.ai scored 0.62. Same product, different machine comprehension."

---

## The Evidence (1:20 — 1:35)

Click the **Evidence** or **Findings** tab.

> "Every decision is content-addressed. SHA-256 receipt over the entire chain — intent hash, inventory snapshot, evidence vector, policy version. Not vibes. Cryptographically verifiable."

**Show:** Receipt hash, evidence dimensions, experiment IDs.

---

## The Research (1:35 — 1:55)

> "This isn't a vibe check. It's built on 16 experiments across 7+ model families.
>
> Six key findings:
> 1. Description seduction is family-clustered — some models pick broken tools if descriptions sound enterprise-y
> 2. Selection is contrast-driven, not content-driven
> 3. Serverless LLM inference is non-deterministic — same prompt flips behavior across time windows
> 4. Position primacy dominates SERP choice — 87% pick slot 0
> 5. Tool name style has zero effect when descriptions are clear
> 6. Decoy resistance varies by model
>
> Generator and judge are always separate models. Llama never scores itself."

**Show:** Research section or experiment results.

---

## The name.com Integration (1:55 — 2:10)

> "name.com isn't just a search API here. It's the full lifecycle:
> - Search for candidates
> - Check availability
> - Get live pricing
> - Register the domain
> - Create DNS records
> - Read DNS back to verify
>
> Six endpoints. Real prices. Real registration. Real DNS. The agent doesn't just recommend — it acquires and configures."

**Show:** name.com endpoints table or the registration steps in the demo.

---

## The Moat (2:10 — 2:25)

> "The moat: measurement compounds. Every experiment, every blind test, every agent inference builds a dataset of what names work for which agent families.
>
> This dataset is sellable. Domain registrars need it. Brand agencies need it. Anyone deploying an agent-facing service needs it.
>
> DomainArena owns the pre-acquisition measurement layer. Before deployment, which name should the machine audience see?"

---

## The Close (2:25 — 2:30)

> "Measure the name. Buy the evidence-backed winner. Verify the infrastructure."

---

## Tab Order (matches presentation flow)

| Tab | When | What judges see |
|-----|------|----------------|
| **Demo** | 0:35 | Streaming logs, 9-step pipeline |
| **Evidence** | 1:20 | Receipt, provenance chain |
| **Findings** | 1:35 | 6 research findings |
| **Frontier** | 1:55 | Agent Readiness positioning |

---

## Key Numbers

| Number | Value |
|--------|-------|
| name.com endpoints | 6 (search, checkAvailability, getPricing, register, DNS create, DNS readback) |
| Experiments | 16 across 7+ model families |
| Tests | 148 passing |
| Inference model | Llama 3.3 70B (blind) |
| Evaluator model | Mistral Small 3.1 (independent) |
| Evidence dimensions | 7 (comprehension, length, TLD, price, category, family, measured) |
| MCP tools | 9 + 2 resources |
| Intent (demo) | "JSON repair API for AI agents that validates and repairs malformed JSON" |

---

## What Judges Should Feel

1. **This is a real problem** — agents discover services by name, nobody measures if they understand it
2. **name.com is causal** — remove it and the system can't search, price, register, or configure
3. **The demo has a real behavioral consequence** — the measured winner differs from the human favorite
4. **It's research-backed** — 16 experiments, not a vibe check
5. **The moat is real** — measurement compounds and is sellable

---

## If Asked About Market Size

- **Domain registrars:** Namecheap, GoDaddy, Google Domains — need agent-comprehension data
- **Brand agencies:** Naming firms need objective measurement beyond "sounds good"
- **Agent-facing services:** Every SaaS, API, tool needs a name agents understand
- **AEO (Agent Experience Optimization):** Emerging field, DomainArena is the measurement layer

---

## If Asked About Competition

- **Name generators:** Generate names, don't test them against agents
- **SEO tools:** Optimize for Google, not for AI agents
- **Domain registrars:** Show availability and price, not comprehension
- **Cloudflare Agent Readiness:** Measures deployed sites, not pre-acquisition names

DomainArena is the only system that blind-tests domain names against AI agents and acquires the winner through name.com.

---

## The name.com Story (for judges)

- **Why name.com?** Without it, DomainArena can measure but can't act. name.com closes the loop: search → price → register → DNS → verify.
- **Which endpoints?** All 6: search, checkAvailability, getPricing, register, DNS create, DNS readback
- **What's special?** Real-time inventory, real prices, real registration. Not a mock. The domain is actually acquired.
- **Fail-closed?** Fresh recheck before registration. If availability or price changed, abort.
- **DNS verification?** Read-back after write. If DNS doesn't match, the configuration failed.

---

## Recording Checklist

- [ ] Landing page loads at `/`
- [ ] "Try the Live Demo" goes to `/demo`
- [ ] Demo tab: Run Demo → logs stream → receipt appears
- [ ] Evidence tab: receipt hash, provenance chain
- [ ] Findings tab: 6 research findings
- [ ] No loading spinners stuck
- [ ] No "click run demo first" text
- [ ] All timestamps correct
- [ ] name.com calls visible in logs (real API, not mock)
- [ ] SHA-256 receipt visible at end
