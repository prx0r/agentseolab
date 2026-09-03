# Domain Intelligence Lab

Reusable infrastructure for experimentally measuring how search-capable agents discover, select, and act on domains and machine-readable web properties.

## Scientific principle

Do not infer agent-search behavior only by asking a model what it *would* search for.

Use two evidence tiers:

1. **Field trials (primary descriptive evidence)** — give an agent the actual user intent plus real search/browse tools and log the queries it actually issues, returned results, opens, citations, and final choice.
2. **Controlled lab trials (causal evidence)** — hold everything constant except one manipulated variable such as hostname, title, description, URL path, schema markup, MCP tool name, or OpenAPI wording.

Hypothetical query generation, rationales, and suggested domains are useful exploratory signals, but not ground truth.

## Required anti-bias controls

- Freeze an immutable SiteIntent before generating domains.
- Separate generator and judge calls.
- Randomize candidate order.
- Repeat pairwise trials with reversed ordering.
- Keep snippets identical in hostname-only tests.
- Use fresh sessions and log model/provider/version/settings.
- Pre-register hypotheses and primary metrics before looking at results.
- Maintain held-out intents and time-based holdouts.
- Report confidence intervals and raw sample counts.
- Never collapse all models into one score without model-family breakdowns.
- Store immutable observations; derive scores as rebuildable projections.
- Distinguish lab preference from real search visibility.
- Treat explanations as coded self-reports, not hidden causal truth.

## Core flow

SiteIntent
  -> field search traces
  -> candidate generation
  -> authoritative availability
  -> blinded preference tournaments
  -> controlled SERP/content experiments
  -> human pairwise feedback
  -> registrar/deployment outcomes
  -> real discovery/invocation outcomes
  -> evidence library

## Domain availability

DNS is only a cheap signal. It cannot prove availability. Use:

syntax/public suffix -> DNS -> RDAP/registry evidence -> registrar authoritative availability -> optional second provider

Return one of AVAILABLE, TAKEN, RESERVED, PREMIUM, UNKNOWN with evidence and timestamps.

## Running the reference CLI

```bash
python -m agentseo_lab.cli init-db ./lab.db
python -m agentseo_lab.cli create-intent ./lab.db examples/site_intent.json
python -m agentseo_lab.cli create-experiment ./lab.db examples/hostname_experiment.json
python -m agentseo_lab.cli report ./lab.db
```

This package deliberately separates experiment/event storage from provider-specific model/search adapters. A worker can ingest traces from OpenAI, Anthropic, Google, Qwen, DeepSeek, Hermes/browser agents, or recorded human sessions using the same event schema.
