# DomainArena — WORD4WORD SCRIPT

**How to read:** Bold text = what you say out loud. [Brackets] = what you do on screen.
Speak slowly. Pause at each section break. Let the demo breathe.

---

## OPENING — [hero visible]

Welcome to DomainArena.

DomainArena explores A/B testing domain names against AI agents.

This matters because the customers discovering your service are increasingly machines, not humans. Ninety-three percent of Google searches now end without a click. AI Overviews answer directly. Agents are making billions of API calls daily, discovering services through domain names.

But here's the problem: nobody tells you whether the agent actually understands your domain name.

---

## PROBLEM — [scroll to "The Problem"]

A human sees jsonrepair.dev and thinks — obviously a JSON tool. An agent sees the same name and might think repair shop. Or JSON documentation. Or nothing useful.

The name that sounds best to humans isn't necessarily the one agents understand. And nobody measures the difference before you buy the domain.

---

## SOLUTION — [scroll to "How It Works"]

Here's what we built.

We freeze your product intent. We search name.com for available candidates. Then we blind-test each domain against Llama 3.3 seventy-billion — no context, no description, just the name.

An independent Mistral evaluator scores whether the agent inferred the right product. The measured winner isn't the human favorite. It's the agent-tested winner.

The full system also registers the domain, configures DNS, and generates a cryptographic receipt. Today we're showing the core measurement pipeline.

---

## NAME.COM — [scroll to sponsor section]

Six name.com endpoints. Real prices. Real availability.

The demo uses search and pricing. The full system also handles availability checks, registration, DNS creation, and DNS readback to verify configuration landed.

This isn't a mock. The prices are live. The availability is real. The agent doesn't just score names — it acquires and configures them.

---

## RESEARCH — [scroll to findings]

This isn't a vibe check. It's built on sixteen experiments across seven-plus model families.

Description seduction is family-clustered. Serverless inference is non-deterministic — the same prompt flips behavior across time windows. Position primacy dominates — eighty-seven percent pick slot zero.

Generator and judge are always separate models. Llama never scores itself.

---

## DEMO — [click "Run Demo"]

Let me show you live.

*[Click "Run Demo"]*

One click. DomainArena takes a product intent — a JSON repair API for AI agents — extracts keywords, and searches name.com for available domains.

*[Discovery results appear — table of domains with live pricing]*

Eight domains returned with live pricing. jsonrepair.com at twelve ninety-nine a year. jsonrepair.org at eight forty-nine. Real prices, real availability.

Now each domain is blind-tested. Llama sees only the hostname — no description, no context. What does this agent think this domain means?

*[Scores stream in — green for match, red for miss]*

Then an independent Mistral evaluator scores whether the inference matches the intent. Generator and judge are always separate models. Llama never scores itself.

*[Winner card appears]*

The measured winner: jsonrepair.com. Agent comprehension: high. The agent correctly infers "JSON repair tool" from the name alone. That's domain legibility you can measure before you spend a dollar.

The entire pipeline — search, blind inference, independent scoring — ran in seconds. No human intuition. No gut feeling. Just evidence.

This is the simplistic demo. One intent, one search, two models. But the architecture scales.

---

## FUTURE — [stay on winner card or scroll to hero]

What does the full version look like?

Cross-family replication. Not just Llama and Mistral — test across Qwen, Gemini, Claude, Command R. If a domain only reads well on one model family, that's a boundary condition, not a law. DomainArena runs the same test across seven-plus families and only promotes a name when the signal is consistent.

Tool calling experiments. Agents don't just read domain names — they discover tools through them. DomainArena measures whether an agent, given a domain name and nothing else, can correctly route to the right API endpoint. That's the real test: not "what do you think this means?" but "can you find the service behind it?"

Paired comparison. AB/BA position-randomized pairwise testing. Bradley-Terry aggregation across dozens of candidates. Not one-shot scoring — statistically powered ranking that controls for position bias.

Execution-grounded validation. Blind inference is the cheap filter. Execution testing is ground truth. Can the agent actually call the service, get a valid response, and complete the task? DomainArena is building toward that.

Real-world outcome tracking. Does the domain that scores highest actually get more traffic from agent-driven discovery?闭环 feedback from deployment back to measurement.

Every experiment adds to a dataset that compounds. The first measurement is expensive. The hundredth is a dataset nobody else has — agent comprehension signals across model families, name types, and TLDs. That's the moat.

---

## CLOSE — [stay on winner card]

Here's the question I want you to think about: would you rather test the name before you buy it, or buy it and hope the machines find you?

The obvious customers: domain registrars who need agent-comprehension data. Namecheap, GoDaddy, Google Domains — every one of them sells names to humans. None of them measure whether agents understand those names. That's a gap.

But it goes further. Every SaaS company choosing a domain for an agent-facing API. Every startup naming a developer tool. Every brand agency pitching a new identity. They all make this decision on gut feeling. DomainArena makes it measurable.

One blind test becomes reusable intelligence for every naming decision that follows. Cross-family replication. Tool calling validation. Execution-grounded testing. The first measurement is expensive. The tenth is free. The hundredth is a dataset nobody else has.

The name that sounds best to humans isn't necessarily the one agents understand. Now you can measure the difference. Before you buy.

*[End — pause 3 seconds]*
