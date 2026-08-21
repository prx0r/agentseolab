// Scientific models for agent preference testing
// Following SCIENTIFIC_METHOD.md exactly

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

// === IMMUTABLE SITE INTENT ===
// Must be captured BEFORE candidate generation
// All downstream observations reference intent_id and intent_hash

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SiteIntent {
    pub purpose: String,
    pub primary_job: String,
    pub audiences: Vec<String>,
    pub capabilities: Vec<String>,
    pub geographic_scope: Option<String>,
    pub language: String,
    pub commercial_model: Option<String>,
    pub constraints: HashMap<String, serde_json::Value>,
    pub prohibited_meanings: Vec<String>,
    pub desired_tld: Option<String>,
    pub desired_length: Option<u32>,
    pub desired_word_rules: Option<String>,
}

impl SiteIntent {
    pub fn to_record(&self) -> SiteIntentRecord {
        let value = serde_json::to_value(self).unwrap();
        let hash = canonical_hash(&value);
        SiteIntentRecord {
            intent_id: new_id("intent"),
            intent_hash: hash,
            created_at: now(),
            payload: self.clone(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SiteIntentRecord {
    pub intent_id: String,
    pub intent_hash: String,
    pub created_at: String,
    pub payload: SiteIntent,
}

// === FIELD TRIAL ===
// Observe actual search behavior, not hypothetical

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FieldTrial {
    pub trial_id: String,
    pub intent_id: String,
    pub agent_model: String,
    pub agent_version: String,
    pub provider: String,
    pub session_id: String,
    pub started_at: String,
    pub completed_at: Option<String>,
    pub search_queries: Vec<SearchQuery>,
    pub final_action: Option<String>,
    pub task_success: Option<bool>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchQuery {
    pub query_id: String,
    pub query_text: String,
    pub query_order: u32,
    pub results_returned: Vec<SearchResult>,
    pub result_opened: Option<String>,
    pub reformulation: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub rank: u32,
    pub title: String,
    pub url: String,
    pub domain: String,
    pub snippet: Option<String>,
}

// === CONTROLLED LAB TRIAL ===
// Isolate causal variables

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LabTrial {
    pub trial_id: String,
    pub experiment_id: String,
    pub treatment: Treatment,
    pub agent_model: String,
    pub agent_version: String,
    pub provider: String,
    pub session_id: String,
    pub candidate_order: Vec<String>,
    pub chosen: Option<String>,
    pub abstained: bool,
    pub timestamp: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Treatment {
    pub treatment_type: String,  // "hostname_only", "snippet", "machine_readable"
    pub variables: HashMap<String, serde_json::Value>,
}

// === PAIRWISE PREFERENCE ===
// Store raw comparisons, not ratings

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PairwiseComparison {
    pub comparison_id: String,
    pub experiment_id: String,
    pub candidate_a: String,
    pub candidate_b: String,
    pub ordering: String,  // "AB" or "BA"
    pub chosen: String,
    pub abstained: bool,
    pub agent_model: String,
    pub agent_version: String,
    pub provider: String,
    pub session_id: String,
    pub timestamp: String,
}

// === EXPLANATION ===
// Structured reason codes, not free-form

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Explanation {
    pub explanation_id: String,
    pub comparison_id: String,
    pub chosen: String,
    pub reason_codes: Vec<String>,
    pub brief_rationale: String,
    pub runner_up: Option<String>,
    pub runner_up_weaknesses: Vec<String>,
    pub challenger_suggestions: Vec<String>,
}

// Valid reason codes
pub const VALID_REASON_CODES: &[&str] = &[
    "SEMANTIC_MATCH",
    "ACTION_ORIENTED",
    "SHORT",
    "PRONOUNCEABLE",
    "KNOWN_TECH_TERM",
    "LOW_AMBIGUITY",
    "TRUST_SIGNAL",
    "TLD_SIGNAL",
    "HTTP_ASSOCIATION",
    "MEMORABLE",
    "BROAD_SCOPE",
    "AGENT_NATIVE",
    "DEVELOPER_NATIVE",
];

// === HYPOTHESIS ===
// For evidence library

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Hypothesis {
    pub hypothesis_id: String,
    pub statement: String,
    pub status: String,  // "replicated", "provisional", "failed"
    pub effect_estimate: Option<f64>,
    pub confidence_interval: Option<(f64, f64)>,
    pub sample_size: u32,
    pub model_families: Vec<String>,
    pub intents: Vec<String>,
    pub date_range: (String, String),
    pub preregistered: bool,
    pub evidence_ids: Vec<String>,
}

// === OUTCOME HIERARCHY ===
// Evidence strength ranking

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum OutcomeLevel {
    ModelRationale,
    RepeatedControlledChoice,
    CrossModelChoice,
    HumanPreference,
    RegistrarClick,
    RegistrationTransition,
    Deployment,
    RealRetrieval,
    ActualInvocation,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Outcome {
    pub outcome_id: String,
    pub intent_id: String,
    pub candidate_id: Option<String>,
    pub level: OutcomeLevel,
    pub evidence: String,
    pub timestamp: String,
    pub confidence: f64,
}
