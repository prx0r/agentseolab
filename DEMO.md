# DomainArena Demo — Recording Guide

## Fixed Demo Intent

Use this exact intent for all rehearsals and the final recording:

```
An API for AI agents to verify JSON, repair malformed JSON and return the corrected machine-readable result.
```

Budget: $15/year first year, $25/year renewal.

## Environment Variables

```bash
# Required for live mode
export NAMECOM_USERNAME="your-username"
export NAMECOM_TOKEN="your-token"
export NAMECOM_MODE="sandbox"

# Optional: Cloudflare for model inference
export CLOUDFLARE_ACCOUNT_ID="..."
export CLOUDFLARE_API_TOKEN="..."

# Write guard — OFF for rehearsal, ON for final take
export DOMAINARENA_ALLOW_WRITES=0   # rehearsal
export DOMAINARENA_ALLOW_WRITES=1   # final recording
```

## Rehearsal Mode (writes disabled)

```bash
# Steps 1-5 work freely, registration/DNS blocked
DOMAINARENA_ALLOW_WRITES=0 python -m domainarena.web.demo
```

Registration attempts will show:
```
WRITE BLOCKED — set DOMAINARENA_ALLOW_WRITES=1 to allow name.com registration
```

## Final Recording Mode (writes enabled)

```bash
# Only enable for the intended final take
DOMAINARENA_ALLOW_WRITES=1 python -m domainarena.web.demo
```

## Recording Script (2:15-2:45)

### 0:00-0:15 — Problem
Show DomainArena home screen.
> "Domain names were designed for humans. But agents increasingly discover, choose and invoke services themselves. We wanted to know: does an AI agent actually understand what a domain name means?"

### 0:15-0:35 — Intent + name.com discovery
Enter frozen demo intent. Show LIVE badge and name.com search trace.
> "I give DomainArena the product intent and budget. name.com provides the live candidate inventory, availability and pricing."

### 0:35-1:00 — Semantic inversion
Show blind model inference. Show one good and one poor inference.
> "Instead of asking an LLM whether a domain sounds nice, we remove the product description and ask multiple agents what they think actually lives behind each domain."

### 1:00-1:15 — Evidence-based recommendation
Show winner with cross-family score.
> "A separate evaluator compares those blind interpretations against the frozen intent. The tested model never scores itself."

### 1:15-1:35 — Fresh checkout
Show fresh name.com availability and price.
> "Before any irreversible action, DomainArena checks name.com again. If availability changed, price moved outside budget, or evidence is missing, it fails closed."

### 1:35-1:50 — Human approval
Click approve.
> "Recommendation is autonomous. Purchase authority is not. A human approves the final spend."

### 1:50-2:10 — Register + DNS
Show registration and DNS setup.
> "name.com registers the selected domain, DomainArena configures DNS, then reads the DNS back instead of assuming the write succeeded."

### 2:10-2:25 — Receipt
Show verified receipt and API trace.
> "The result is a verified domain lifecycle: search, measure, approve, acquire, configure and prove."

### 2:25-2:40 — Research/future
> "This grew out of 16 experiments across seven-plus model families showing that agents are vulnerable to description bias, position effects and model-specific interpretations. DomainArena is the first step toward measuring agent legibility as a property of internet infrastructure."

## Fallback Path

If Cloudflare inference is slow during recording:
1. Use fixture mode for the semantic inversion step
2. Show the live name.com search/checkout steps
3. narrate that inference was pre-computed

## Post-Recording

1. Verify the receipt hash is valid
2. Check DNS read-back succeeded
3. Screenshot the final receipt for Devpost
4. Upload video immediately
