# HydraDB-Native Architecture for AgentSEOLab

## Graph Schema

### Node Types

```cypher
// Core entities
(:SiteIntent {id, purpose, primary_job, audiences, capabilities, constraints, language, created_at})
(:Experiment {id, intent_id, kind, hypothesis_id, preregistered, created_at})
(:Observation {id, experiment_id, intent_id, evidence_tier, event_type, model_family, model_version, provider, session_id, created_at})
(:Candidate {id, intent_id, domain, created_at})
(:DomainCheck {id, candidate_id, domain, status, confidence, checked_at})
(:Outcome {id, intent_id, candidate_id, outcome_type, created_at})
(:Hypothesis {id, statement, status, primary_metric, created_at})

// Capability graph
(:Capability {id, name, description, category, status})
(:Tool {id, name, capability_id, version, status})
(:Site {id, name, domain, lifecycle})
(:Standard {id, version, status})

// Agent behavior
(:Agent {id, name, model_family, model_version})
(:SearchQuery {id, query, intent_id, timestamp})
(:Selection {id, query_id, candidate_id, position, chosen})
(:Preference {id, agent_id, candidate_a, candidate_b, winner})
```

### Edge Types

```cypher
// Experiment lineage
(:SiteIntent)-[:GENERATED]->(:Candidate)
(:Experiment)-[:TESTS]->(:SiteIntent)
(:Experiment)-[:USES]->(:Observation)
(:Observation)-[:PRODUCES]->(:Outcome)
(:Experiment)-[:VALIDATES]->(:Hypothesis)

// Capability graph
(:Capability)-[:IMPLEMENTED_BY]->(:Tool)
(:Tool)-[:EXPOSED_BY]->(:Site)
(:Site)-[:CONFORMS_TO]->(:Standard)
(:Capability)-[:DEPENDS_ON]->(:Capability)

// Agent behavior
(:Agent)-[:ISSUED]->(:SearchQuery)
(:SearchQuery)-[:RESULTED_IN]->(:Selection)
(:Selection)-[:PREFERRED]->(:Candidate)
(:Agent)-[:PREFERS]->(:Preference)
```

## HydraDB Connection

```rust
// HTTP API endpoint
const HYDRA_URL: &str = "http://127.0.0.1:8443";
const HYDRA_TOKEN: &str = "local-development-token-32-bytes";
const HYDRA_NAMESPACE: &str = "default";
const HYDRA_GRAPH_ID: &str = "agentseolab";
const HYDRA_CELL_ID: &str = "cell-0";
```

## OpenCypher Queries

### Create SiteIntent
```cypher
CREATE (si:SiteIntent {
  id: $id,
  purpose: $purpose,
  primary_job: $primary_job,
  audiences: $audiences,
  capabilities: $capabilities,
  constraints: $constraints,
  language: $language,
  created_at: $created_at
})
```

### Create Experiment
```cypher
CREATE (e:Experiment {
  id: $id,
  intent_id: $intent_id,
  kind: $kind,
  hypothesis_id: $hypothesis_id,
  preregistered: $preregistered,
  created_at: $created_at
})
MATCH (si:SiteIntent {id: $intent_id})
CREATE (e)-[:TESTS]->(si)
```

### Record Observation
```cypher
CREATE (o:Observation {
  id: $id,
  experiment_id: $experiment_id,
  intent_id: $intent_id,
  evidence_tier: $evidence_tier,
  event_type: $event_type,
  model_family: $model_family,
  model_version: $model_version,
  provider: $provider,
  session_id: $session_id,
  created_at: $created_at
})
MATCH (e:Experiment {id: $experiment_id})
CREATE (o)-[:PRODUCED_BY]->(e)
```

### Query Agent Preferences
```cypher
MATCH (a:Agent)-[:PREFERS]->(p:Preference)-[:PREFERRED]->(c:Candidate)
WHERE p.winner = c.id
RETURN c.domain, count(p) as preference_count
ORDER BY preference_count DESC
```

### Query Capability Graph
```cypher
MATCH (cap:Capability)-[:IMPLEMENTED_BY]->(tool:Tool)-[:EXPOSED_BY]->(site:Site)
RETURN cap.name, tool.name, site.name
```

### Find Missing Capabilities
```cypher
MATCH (cap:Capability)
WHERE NOT ()-[:IMPLEMENTED_BY]->(cap)
RETURN cap.name, cap.description
```
