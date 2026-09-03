# DomainArena — NORTHSTAR PROMPT

## Assessment Criteria Alignment

**Progress:** 16 experiments across 7+ model families. 148 tests. Live 9-step pipeline: name.com search → pricing → blind inference → independent judge → recommendation → fresh recheck → register → DNS → receipt. Cloudflare Workers AI with real models.

**Concept:** Domain names were designed for humans. Agents increasingly discover services by name. Nobody measures if the agent actually understands the domain. This is the pre-acquisition measurement layer.

**Feasibility:** Natural extension of domain registration. Namecheap, GoDaddy, Google Domains all need this. Brand agencies need objective measurement. DomainArena owns the measurement layer that makes domain naming data-driven for the machine audience.

## Structure

1. Welcome + statistic (10s)
2. Problem (15s)
3. Solution thesis (15s)
4. Landing page scroll — pipeline + research (30s)
5. Demo — narrate as it runs (60s)
6. Post-demo: startup potential, moat, revenue (30s)
7. Close (10s)

## Shocking Statistic
"Ninety-three percent of Google searches now end without a click. The thing discovering your service is increasingly a machine, not a human. And nobody tells you whether that machine understands your domain name."

---

# DomainArena — WORD4WORD SCRIPT

**Total: ~2:20 speaking time + demo pauses = ~2:45 recording**

---

## [LANDING PAGE — HERO]

Welcome to DomainArena.

DomainArena explores A/B testing domain names against AI agents — which has become increasingly relevant as the customers discovering your service are increasingly machines, not humans.

Ninety-three percent of Google searches now end without a click. AI Overviews answer directly. Meanwhile, agents are making billions of API calls daily, discovering services through domain names.

Here's the problem: a human sees jsonrepair.dev and thinks, obviously a JSON tool. An agent sees the same name and might think repair shop, or JSON documentation, or nothing useful.

The name that sounds best to humans isn't necessarily the one agents understand. And nobody measures the difference before you buy the domain.

---

## [SCROLL TO PROBLEM SECTION]

Let me show you what we built.

We freeze your product intent. We search name.com for available candidates. Then we blind-test each domain against Llama 3.3 seventy-billion — no context, no description, just the name.

An independent Mistral evaluator scores whether the agent inferred the right product. The measured winner isn't the human favorite. It's the agent-tested winner.

Then we buy it through name.com. Configure DNS. Verify it works. The entire lifecycle from discovery to deployment.

---

## [SCROLL TO HOW IT WORKS — pipeline section]

Six name.com endpoints. Real prices. Real registration. Real DNS.

Search for candidates. Check availability. Get live pricing. Register the domain. Create DNS records. Read DNS back to verify.

This isn't a mock. The domain is actually acquired. The agent doesn't just recommend — it acquires and configures.

---

## [SCROLL TO FINDINGS — research section]

This isn't a vibe check. It's built on sixteen experiments across seven-plus model families.

Description seduction is family-clustered — some models pick broken tools if descriptions sound enterprise-y. Serverless inference is non-deterministic — the same prompt flips behavior across time windows. Position primency dominates — eighty-seven percent pick slot zero.

Generator and judge are always separate models. Llama never scores itself. That's scientific rigor, not a demo trick.

---

## [CLICK TRY THE LIVE DEMO → /demo]

Let me show you.

*[Click Search name.com inventory — narrate as it runs]*

I give DomainArena a product intent: a JSON repair API for AI agents. Name.com searches for available domains matching the intent.

Nine search queries across dot-com, dot-dev, dot-ai. Name.com returns five candidates with live pricing — eight forty-nine to sixteen forty-nine per year.

*[Click Run blind agent comprehension test]*

Now each domain is tested blind. Llama 3.3 sees only the name — no description, no context. Then Mistral evaluates whether the inference matches the intent.

Scores: 0.85, 0.8, 0.8, 0.8, 0.8. The agent understands all of them — but jsonrepair.com scored highest at 0.85.

*[Click View recommendation]*

The measured winner: jsonrepair.com. Agent comprehension: 0.85. Purchase: twelve ninety-nine per year.

*[Click Approve and register]*

DomainArena calls name.com again — fresh recheck. Available. Twelve ninety-nine. Then registers. Creates DNS. Reads it back to verify.

*[Let the receipt appear]*

The entire decision frozen into a cryptographic receipt. Measured, approved, acquired, configured, verified.

---

## [CLOSE]

DomainArena A/B tests domain names for the machine audience. Measures comprehension before purchase. Then buys and configures the winner through name.com.

The obvious customers: domain registrars who need agent-comprehension data. Brand agencies who need objective measurement. Anyone deploying an agent-facing service.

One measurement becomes reusable intelligence for every naming decision that follows.

Measure the name. Buy the evidence-backed winner. Verify the infrastructure.

*[End]*
