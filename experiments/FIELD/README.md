# Field Trials — Real Agent Behavior Observation

## Purpose
Observe actual agent search/browse/select behavior on frozen SiteIntents using real hermes sessions. The TRACE is ground truth — never ask the agent why it chose something.

## Event Ontology (strict separation, never collapse)
SEARCH_RESULT_EXPOSED / OPENED / SOURCE_READ / USED / CITED /
CAPABILITY_SELECTED / INVOKED / EXECUTION_SUCCEEDED / TASK_VERIFIED

## ⚠️ task_success ≠ citation presence
Historical task_success computed from URL-in-final-answer measured FINAL_URL_REPORTED.
All such observations are INVALIDATED per dev plan P0.

## Known Gap
All field subjects (S1-S3) use mimo-v2.5/opencode-go — violates multi-family field repetition rule from SCIENTIFIC_METHOD.md.

## Current Data
8 field traces from F-001 intent across scout/curator/patala profiles.

## Status: PROTOCOL DESIGNED, SCALING IN PROGRESS via hermes builder
