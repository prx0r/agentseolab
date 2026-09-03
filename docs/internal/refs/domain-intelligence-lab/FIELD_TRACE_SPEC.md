# Field Trace Specification

A field run gives the agent a task and its ordinary search/browser tools.

Capture observable events in order:

```json
{"event_type":"search_query","payload":{"query":"free API domain availability"}}
{"event_type":"search_results","payload":{"query_id":"...","results":[{"rank":1,"url":"...","title":"...","description":"..."}]}}
{"event_type":"result_open","payload":{"url":"...","rank":1}}
{"event_type":"citation","payload":{"url":"..."}}
{"event_type":"final_choice","payload":{"domain":"...","action":"investigate"}}
```

Do not request or persist private chain-of-thought. If the model supplies a concise explicit rationale after a decision, record it separately as a `rationale` observation.

## Search experiment isolation

For domain-name inference, the agent must not see generated candidate domains before its initial search trace.

For real-world visibility tests, do not force equal rankings: ranking/retrieval is part of the phenomenon.

For causal hostname tests, use the controlled lab protocol instead and keep snippets/content equal.
