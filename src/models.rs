use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashMap;
use uuid::Uuid;

pub fn now() -> String {
    Utc::now().to_rfc3339()
}

pub fn new_id(prefix: &str) -> String {
    format!("{}_{}", prefix, Uuid::new_v4().to_string().replace('-', ""))
}

pub fn canonical_hash(obj: &serde_json::Value) -> String {
    let json = serde_json::to_string(obj).unwrap_or_default();
    let mut hasher = Sha256::new();
    hasher.update(json.as_bytes());
    format!("{:x}", hasher.finalize())
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SiteIntent {
    pub purpose: String,
    pub primary_job: String,
    pub audiences: Vec<String>,
    pub capabilities: Vec<String>,
    pub constraints: HashMap<String, serde_json::Value>,
    #[serde(default = "default_language")]
    pub language: String,
    pub metadata: Option<HashMap<String, serde_json::Value>>,
}

fn default_language() -> String {
    "en".to_string()
}

impl SiteIntent {
    pub fn record(&self) -> HashMap<String, serde_json::Value> {
        let mut map = serde_json::to_value(self).unwrap().as_object().unwrap().clone();
        let hash = canonical_hash(&serde_json::Value::Object(map.clone()));
        map.insert("intent_id".to_string(), serde_json::Value::String(new_id("intent")));
        map.insert("intent_hash".to_string(), serde_json::Value::String(hash));
        map.insert("created_at".to_string(), serde_json::Value::String(now()));
        map.into_iter().collect()
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Experiment {
    pub experiment_id: String,
    pub intent_id: String,
    pub created_at: String,
    pub kind: String,
    pub hypothesis_id: Option<String>,
    pub preregistered: bool,
    pub payload: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Observation {
    pub observation_id: String,
    pub experiment_id: Option<String>,
    pub intent_id: String,
    pub created_at: String,
    pub evidence_tier: String,
    pub event_type: String,
    pub model_family: Option<String>,
    pub model_version: Option<String>,
    pub provider: Option<String>,
    pub session_id: Option<String>,
    pub payload: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Candidate {
    pub candidate_id: String,
    pub intent_id: String,
    pub domain: String,
    pub created_at: String,
    pub parent_ids: Vec<String>,
    pub generator: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DomainCheck {
    pub check_id: String,
    pub candidate_id: String,
    pub domain: String,
    pub checked_at: String,
    pub status: String,
    pub confidence: f64,
    pub evidence: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Outcome {
    pub outcome_id: String,
    pub intent_id: String,
    pub candidate_id: Option<String>,
    pub created_at: String,
    pub outcome_type: String,
    pub payload: HashMap<String, serde_json::Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Hypothesis {
    pub hypothesis_id: String,
    pub created_at: String,
    pub statement: String,
    pub status: String,
    pub primary_metric: Option<String>,
    pub payload: HashMap<String, serde_json::Value>,
}
