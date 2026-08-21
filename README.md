# AgentSEOLab — Domain Intelligence Lab

> Rust experiment infrastructure for measuring how search-capable agents discover, select, and act on domains and machine-readable web properties.

## What it does

Runs controlled experiments to measure:
- Agent preference for domain names
- Search-result selection behavior
- Human vs agent preference differences
- Domain demand patterns

## Quick start

```bash
# Build
cargo build --release

# Initialize database
./target/release/agentseolab init-db lab.db

# Create intent
./target/release/agentseolab create-intent lab.db intent.json

# Create experiment
./target/release/agentseolab create-experiment lab.db experiment.json

# Ingest observation
./target/release/agentseolab ingest-observation lab.db observation.json

# Generate report
./target/release/agentseolab report lab.db
```

## Architecture

```
agentseolab/
├── src/
│   ├── main.rs       # CLI
│   ├── models.rs     # SiteIntent, Experiment, Observation
│   └── db.rs         # SQLite database
├── docs/             # Scientific method, evidence library
├── schemas/          # Observation schema
└── examples/         # Intent and experiment templates
```

## Scientific Principle

Do not infer agent-search behavior only by asking a model what it *would* search for.

Use two evidence tiers:
1. **Field trials** — give an agent real tools and log what it actually does
2. **Controlled lab trials** — hold everything constant except one variable

## Anti-Bias Controls

- Freeze immutable SiteIntent before generating candidates
- Separate generator and judge calls
- Randomize candidate order
- Repeat pairwise trials with reversed ordering
- Use fresh sessions and log model/provider/version
- Store immutable observations; derive scores as projections

## Integration

This project integrates with:
- **domainnamechecker** — domain verification and availability
- **agentseo** — codebase optimization
- **finalbuilds2** — control plane orchestration
