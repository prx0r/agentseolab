// Capability Registry — data structures for capability catalog.
// HydraDB integration deferred (see BUILD_ORDER.md Phase E).

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Capability {
    pub id: String,
    pub name: String,
    pub description: String,
    pub category: String,
    pub status: String,
    pub interfaces: Vec<String>,
    pub pricing: String,
    pub performance: Option<PerformanceMetrics>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PerformanceMetrics {
    pub p50_ms: Option<f64>,
    pub p95_ms: Option<f64>,
    pub success_rate: Option<f64>,
}
