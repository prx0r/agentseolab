# Field Trials — Real Agent Behavior Observation

## Purpose
Observe actual agent search/browse/select behavior on frozen SiteIntents.
No synthetic judgments — the TRACE is ground truth.

## Methodology
1. Freeze SiteIntent BEFORE any candidate generation
2. Give search-capable agent normal search tools only
3. Record observable trace: queries[], results[], opens[], citations[], selections[]
4. Never ask agent "why did you choose X" as ground truth

## Event Ontology (strict separation)
SEARCH_RESULT_EXPOSED / OPENED / SOURCE_READ / USED / CITED /
CAPABILITY_SELECTED / INVOKED / EXECUTION_SUCCEEDED / TASK_VERIFIED

## ⚠️ task_success ≠ citation presence
Historical task_success was computed from URL-in-final-answer.
This measures FINAL_URL_REPORTED, not task success.
All historical observations with this metric are invalidated.

## Current Data
8 field traces from scout/curator/patala profiles on F-001 intent.
All profiles are mimo-v2.5 — violates multi-family requirement.

## Status: PROTOCOL DESIGNED, SCALING IN PROGRESS
