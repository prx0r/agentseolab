# AgentSEO Evidence Library

Derived rules must be rebuildable from observations.

Recommended hypothesis record:

```json
{
  "hypothesis_id":"H-0041",
  "statement":"For API-task intents, an explicit API noun in the result title increases selection probability.",
  "status":"provisional",
  "primary_metric":"selection_probability",
  "effect_estimate":null,
  "confidence_interval":null,
  "n":0,
  "intent_count":0,
  "model_families":[],
  "known_moderators":[],
  "replications":[]
}
```

Use evidence grades:

A — replicated field effect across held-out intents/models
B — replicated controlled causal effect + compatible field evidence
C — controlled experiment only
D — exploratory model/human preference
E — hypothesis/rationale only

Recommendations emitted by an SEO engine should cite hypothesis IDs and grades.
