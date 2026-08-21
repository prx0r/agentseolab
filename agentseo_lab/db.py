import sqlite3, json
SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS intents(
 intent_id TEXT PRIMARY KEY, intent_hash TEXT NOT NULL, created_at TEXT NOT NULL,
 payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS experiments(
 experiment_id TEXT PRIMARY KEY, intent_id TEXT NOT NULL, created_at TEXT NOT NULL,
 kind TEXT NOT NULL, hypothesis_id TEXT, preregistered INTEGER NOT NULL DEFAULT 0,
 payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS observations(
 observation_id TEXT PRIMARY KEY, experiment_id TEXT, intent_id TEXT NOT NULL,
 created_at TEXT NOT NULL, evidence_tier TEXT NOT NULL, event_type TEXT NOT NULL,
 model_family TEXT, model_version TEXT, provider TEXT, session_id TEXT,
 payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS candidates(
 candidate_id TEXT PRIMARY KEY, intent_id TEXT NOT NULL, domain TEXT NOT NULL,
 created_at TEXT NOT NULL, parent_ids_json TEXT, generator_json TEXT,
 UNIQUE(intent_id, domain)
);
CREATE TABLE IF NOT EXISTS domain_checks(
 check_id TEXT PRIMARY KEY, candidate_id TEXT, domain TEXT NOT NULL, checked_at TEXT NOT NULL,
 status TEXT NOT NULL, confidence REAL, evidence_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS outcomes(
 outcome_id TEXT PRIMARY KEY, intent_id TEXT NOT NULL, candidate_id TEXT,
 created_at TEXT NOT NULL, outcome_type TEXT NOT NULL, payload_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS hypotheses(
 hypothesis_id TEXT PRIMARY KEY, created_at TEXT NOT NULL, statement TEXT NOT NULL,
 status TEXT NOT NULL, primary_metric TEXT, payload_json TEXT NOT NULL
);
"""
def connect(path):
    db=sqlite3.connect(path)
    db.executescript(SCHEMA)
    return db
