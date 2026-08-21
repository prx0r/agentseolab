// Scientific database schema for agent preference testing

use anyhow::Result;
use rusqlite::{params, Connection};
use crate::models::*;

const SCHEMA: &str = "
PRAGMA journal_mode=WAL;

-- Immutable SiteIntent (captured BEFORE candidate generation)
CREATE TABLE IF NOT EXISTS site_intents (
    intent_id TEXT PRIMARY KEY,
    intent_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    purpose TEXT NOT NULL,
    primary_job TEXT NOT NULL,
    audiences TEXT NOT NULL,
    capabilities TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'en',
    constraints_json TEXT NOT NULL,
    prohibited_meanings TEXT,
    desired_tld TEXT,
    desired_length INTEGER,
    desired_word_rules TEXT,
    payload_json TEXT NOT NULL
);

-- Field trials (observe actual search behavior)
CREATE TABLE IF NOT EXISTS field_trials (
    trial_id TEXT PRIMARY KEY,
    intent_id TEXT NOT NULL,
    agent_model TEXT NOT NULL,
    agent_version TEXT NOT NULL,
    provider TEXT NOT NULL,
    session_id TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    search_queries_json TEXT NOT NULL,
    final_action TEXT,
    task_success INTEGER,
    FOREIGN KEY (intent_id) REFERENCES site_intents(intent_id)
);

-- Search queries within field trials
CREATE TABLE IF NOT EXISTS search_queries (
    query_id TEXT PRIMARY KEY,
    trial_id TEXT NOT NULL,
    query_text TEXT NOT NULL,
    query_order INTEGER NOT NULL,
    results_json TEXT NOT NULL,
    result_opened TEXT,
    reformulation TEXT,
    FOREIGN KEY (trial_id) REFERENCES field_trials(trial_id)
);

-- Lab trials (controlled experiments)
CREATE TABLE IF NOT EXISTS lab_trials (
    trial_id TEXT PRIMARY KEY,
    experiment_id TEXT NOT NULL,
    treatment_type TEXT NOT NULL,
    treatment_variables_json TEXT NOT NULL,
    agent_model TEXT NOT NULL,
    agent_version TEXT NOT NULL,
    provider TEXT NOT NULL,
    session_id TEXT NOT NULL,
    candidate_order_json TEXT NOT NULL,
    chosen TEXT,
    abstained INTEGER NOT NULL DEFAULT 0,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
);

-- Pairwise comparisons (preference measurement)
CREATE TABLE IF NOT EXISTS pairwise_comparisons (
    comparison_id TEXT PRIMARY KEY,
    experiment_id TEXT NOT NULL,
    candidate_a TEXT NOT NULL,
    candidate_b TEXT NOT NULL,
    ordering TEXT NOT NULL,
    chosen TEXT,
    abstained INTEGER NOT NULL DEFAULT 0,
    agent_model TEXT NOT NULL,
    agent_version TEXT NOT NULL,
    provider TEXT NOT NULL,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
);

-- Explanations (structured reason codes)
CREATE TABLE IF NOT EXISTS explanations (
    explanation_id TEXT PRIMARY KEY,
    comparison_id TEXT NOT NULL,
    chosen TEXT NOT NULL,
    reason_codes TEXT NOT NULL,
    brief_rationale TEXT,
    runner_up TEXT,
    runner_up_weaknesses TEXT,
    challenger_suggestions TEXT,
    FOREIGN KEY (comparison_id) REFERENCES pairwise_comparisons(comparison_id)
);

-- Hypotheses (evidence library)
CREATE TABLE IF NOT EXISTS hypotheses (
    hypothesis_id TEXT PRIMARY KEY,
    statement TEXT NOT NULL,
    status TEXT NOT NULL,
    effect_estimate REAL,
    confidence_interval_json TEXT,
    sample_size INTEGER NOT NULL,
    model_families_json TEXT NOT NULL,
    intents_json TEXT NOT NULL,
    date_range_json TEXT NOT NULL,
    preregistered INTEGER NOT NULL DEFAULT 0,
    evidence_ids_json TEXT
);

-- Outcomes (evidence hierarchy)
CREATE TABLE IF NOT EXISTS outcomes (
    outcome_id TEXT PRIMARY KEY,
    intent_id TEXT NOT NULL,
    candidate_id TEXT,
    level TEXT NOT NULL,
    evidence TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    confidence REAL NOT NULL,
    FOREIGN KEY (intent_id) REFERENCES site_intents(intent_id)
);

-- Experiments (legacy support)
CREATE TABLE IF NOT EXISTS experiments (
    experiment_id TEXT PRIMARY KEY,
    intent_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    kind TEXT NOT NULL,
    hypothesis_id TEXT,
    preregistered INTEGER NOT NULL DEFAULT 0,
    payload_json TEXT NOT NULL,
    FOREIGN KEY (intent_id) REFERENCES site_intents(intent_id)
);

-- Observations (legacy support)
CREATE TABLE IF NOT EXISTS observations (
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
        let record = intent.to_record();
        let audiences = serde_json::to_string(&intent.audiences)?;
        let capabilities = serde_json::to_string(&intent.capabilities)?;
        let constraints = serde_json::to_string(&intent.constraints)?;
        let prohibited = serde_json::to_string(&intent.prohibited_meanings)?;
        let payload = serde_json::to_string(&record)?;
        
        self.conn.execute(
            \"INSERT INTO site_intents (intent_id, intent_hash, created_at, purpose, primary_job, audiences, capabilities, language, constraints_json, prohibited_meanings, desired_tld, desired_length, desired_word_rules, payload_json) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12, ?13, ?14)\",
            params![
                record.intent_id,
                record.intent_hash,
                record.created_at,
                intent.purpose,
                intent.primary_job,
                audiences,
                capabilities,
                intent.language,
                constraints,
                prohibited,
                intent.desired_tld,
                intent.desired_length,
                intent.desired_word_rules,
                payload
            ],
        )?;
        
        Ok(record.intent_id)
    }
    
    pub fn insert_field_trial(&self, trial: &FieldTrial) -> Result<String> {
        let queries = serde_json::to_string(&trial.search_queries)?;
        let final_action = trial.final_action.as_deref();
        let task_success = trial.task_success.map(|b| b as i32);
        
        self.conn.execute(
            \"INSERT INTO field_trials (trial_id, intent_id, agent_model, agent_version, provider, session_id, started_at, completed_at, search_queries_json, final_action, task_success) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)\",
            params![
                trial.trial_id,
                trial.intent_id,
                trial.agent_model,
                trial.agent_version,
                trial.provider,
                trial.session_id,
                trial.started_at,
                trial.completed_at,
                queries,
                final_action,
                task_success
            ],
        )?;
        
        Ok(trial.trial_id.clone())
    }
    
    pub fn insert_pairwise_comparison(&self, comp: &PairwiseComparison) -> Result<String> {
        self.conn.execute(
            \"INSERT INTO pairwise_comparisons (comparison_id, experiment_id, candidate_a, candidate_b, ordering, chosen, abstained, agent_model, agent_version, provider, session_id, timestamp) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11, ?12)\",
            params![
                comp.comparison_id,
                comp.experiment_id,
                comp.candidate_a,
                comp.candidate_b,
                comp.ordering,
                comp.chosen,
                comp.abstained as i32,
                comp.agent_model,
                comp.agent_version,
                comp.provider,
                comp.session_id,
                comp.timestamp
            ],
        )?;
        
        Ok(comp.comparison_id.clone())
    }
    
    pub fn insert_hypothesis(&self, hyp: &Hypothesis) -> Result<String> {
        let ci = serde_json::to_string(&hyp.confidence_interval)?;
        let families = serde_json::to_string(&hyp.model_families)?;
        let intents = serde_json::to_string(&hyp.intents)?;
        let date_range = serde_json::to_string(&hyp.date_range)?;
        let evidence = serde_json::to_string(&hyp.evidence_ids)?;
        
        self.conn.execute(
            \"INSERT INTO hypotheses (hypothesis_id, statement, status, effect_estimate, confidence_interval_json, sample_size, model_families_json, intents_json, date_range_json, preregistered, evidence_ids_json) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8, ?9, ?10, ?11)\",
            params![
                hyp.hypothesis_id,
                hyp.statement,
                hyp.status,
                hyp.effect_estimate,
                ci,
                hyp.sample_size,
                families,
                intents,
                date_range,
                hyp.preregistered as i32,
                evidence
            ],
        )?;
        
        Ok(hyp.hypothesis_id.clone())
    }
    
    pub fn report(&self) -> Result<()> {
        let tables = vec![
            "site_intents", "field_trials", "search_queries", 
            "lab_trials", "pairwise_comparisons", "explanations",
            "hypotheses", "outcomes", "experiments", "observations"
        ];
        for table in &tables {
            let count: i64 = self.conn.query_row(&format!(\"SELECT COUNT(*) FROM {}\", table), [], |row| row.get(0))?;
            println!(\"  {}: {}\", table, count);
        }
        Ok(())
    }
    
    pub fn report_pairwise_stats(&self) -> Result<()> {
        let total: i64 = self.conn.query_row(\"SELECT COUNT(*) FROM pairwise_comparisons\", [], |row| row.get(0))?;
        let abstained: i64 = self.conn.query_row(\"SELECT COUNT(*) FROM pairwise_comparisons WHERE abstained = 1\", [], |row| row.get(0))?;
        
        println!(\"\n📊 Pairwise Comparison Stats:\");
        println!(\"  Total comparisons: {}\", total);
        println!(\"  Abstained: {}\", abstained);
        println!(\"  Valid responses: {}\", total - abstained);
        
        if total > 0 {
            println!(\"\n  By model:\");
            let mut stmt = self.conn.prepare(
                \"SELECT agent_model, COUNT(*) as cnt FROM pairwise_comparisons GROUP BY agent_model ORDER BY cnt DESC\"
            )?;
            let rows = stmt.query_map([], |row| {
                Ok((row.get::<_, String>(0)?, row.get::<_, i64>(1)?))
            })?;
            for row in rows {
                let (model, count) = row?;
                println!(\"    {}: {} comparisons\", model, count);
            }
        }
        
        Ok(())
    }
}
