use anyhow::Result;
use rusqlite::{params, Connection};
use crate::models::*;

const SCHEMA: &str = "
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS intents(
    intent_id TEXT PRIMARY KEY,
    intent_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS experiments(
    experiment_id TEXT PRIMARY KEY,
    intent_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    kind TEXT NOT NULL,
    hypothesis_id TEXT,
    preregistered INTEGER NOT NULL DEFAULT 0,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS observations(
    observation_id TEXT PRIMARY KEY,
    experiment_id TEXT,
    intent_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    evidence_tier TEXT NOT NULL,
    event_type TEXT NOT NULL,
    model_family TEXT,
    model_version TEXT,
    provider TEXT,
    session_id TEXT,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS candidates(
    candidate_id TEXT PRIMARY KEY,
    intent_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    created_at TEXT NOT NULL,
    parent_ids_json TEXT,
    generator_json TEXT,
    UNIQUE(intent_id, domain)
);

CREATE TABLE IF NOT EXISTS domain_checks(
    check_id TEXT PRIMARY KEY,
    candidate_id TEXT,
    domain TEXT NOT NULL,
    checked_at TEXT NOT NULL,
    status TEXT NOT NULL,
    confidence REAL,
    evidence_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS outcomes(
    outcome_id TEXT PRIMARY KEY,
    intent_id TEXT NOT NULL,
    candidate_id TEXT,
    created_at TEXT NOT NULL,
    outcome_type TEXT NOT NULL,
    payload_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS hypotheses(
    hypothesis_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    statement TEXT NOT NULL,
    status TEXT NOT NULL,
    primary_metric TEXT,
    payload_json TEXT NOT NULL
);
";

pub struct Database {
    conn: Connection,
}

impl Database {
    pub fn connect(path: &str) -> Result<Self> {
        let conn = Connection::open(path)?;
        conn.execute_batch(SCHEMA)?;
        Ok(Self { conn })
    }
    
    pub fn insert_intent(&self, intent: &SiteIntent) -> Result<String> {
        let record = intent.record();
        let id = record["intent_id"].as_str().unwrap().to_string();
        let hash = record["intent_hash"].as_str().unwrap().to_string();
        let created_at = record["created_at"].as_str().unwrap().to_string();
        let payload = serde_json::to_string(&record)?;
        
        self.conn.execute(
            "INSERT INTO intents (intent_id, intent_hash, created_at, payload_json) VALUES (?1, ?2, ?3, ?4)",
            params![id, hash, created_at, payload],
        )?;
        
        Ok(id)
    }
    
    pub fn insert_experiment(&self, intent_id: &str, kind: &str, hypothesis_id: Option<&str>, preregistered: bool, payload: &serde_json::Value) -> Result<String> {
        let id = crate::models::new_id("exp");
        let created_at = crate::models::now();
        let payload_json = serde_json::to_string(payload)?;
        
        self.conn.execute(
            "INSERT INTO experiments (experiment_id, intent_id, created_at, kind, hypothesis_id, preregistered, payload_json) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
            params![id, intent_id, created_at, kind, hypothesis_id, preregistered as i32, payload_json],
        )?;
        
        Ok(id)
    }
    
    pub fn insert_observation(&self, experiment_id: Option<&str>, intent_id: &str, evidence_tier: &str, event_type: &str, model_family: Option<&str>, model_version: Option<&str>, provider: Option<&str>, session_id: Option<&str>, payload: &serde_json::Value) -> Result<String> {
        let id = crate::models::new_id("obs");
        let created_at = crate::models::now();
        let payload_json = serde_json::to_string(payload)?;
        
        self.conn.execute(
            "INSERT INTO observations (observation_id, experiment_id, intent_id, created_at, evidence_tier, event_type, model_family, model_version, provider, session_id, payload_json) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)",
            params![id, experiment_id, intent_id, created_at, evidence_tier, event_type, model_family, model_version, provider, session_id, payload_json],
        )?;
        
        Ok(id)
    }
    
    pub fn report(&self) -> Result<()> {
        let tables = ["intents", "experiments", "observations", "candidates", "domain_checks", "outcomes", "hypotheses"];
        for table in &tables {
            let count: i64 = self.conn.query_row(&format!("SELECT COUNT(*) FROM {}", table), [], |row| row.get(0))?;
            println!("  {}: {}", table, count);
        }
        Ok(())
    }
}
