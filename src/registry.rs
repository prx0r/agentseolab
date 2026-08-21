// Capability Registry — stores capabilities in HydraDB graph

use anyhow::Result;
use crate::hydradb::HydraDBClient;
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

pub struct CapabilityRegistry {
    client: HydraDBClient,
}

impl CapabilityRegistry {
    pub fn new(client: HydraDBClient) -> Self {
        Self { client }
    }
    
    pub async fn register_capability(&self, cap: &Capability) -> Result<()> {
        let props = serde_json::json!({
            "id": cap.id,
            "name": cap.name,
            "description": cap.description,
            "category": cap.category,
            "status": cap.status,
            "interfaces": cap.interfaces.join(","),
            "pricing": cap.pricing
        });
        
        self.client.create_entity("Capability", &cap.id, &props).await?;
        println!("✓ Capability registered: {}", cap.id);
        Ok(())
    }
    
    pub async fn register_tool(&self, tool_id: &str, capability_id: &str, name: &str) -> Result<()> {
        let props = serde_json::json!({
            "id": tool_id,
            "name": name,
            "capability_id": capability_id,
            "status": "active"
        });
        
        self.client.create_entity("Tool", tool_id, &props).await?;
        self.client.create_edge("Tool", tool_id, "Capability", capability_id, "IMPLEMENTS").await?;
        println!("✓ Tool registered: {} implements {}", tool_id, capability_id);
        Ok(())
    }
    
    pub async fn find_missing_capabilities(&self) -> Result<Vec<serde_json::Value>> {
        let query = "MATCH (cap:Capability) WHERE NOT ()-[:IMPLEMENTS]->(cap) RETURN cap.id, cap.name, cap.description";
        let result = self.client.query(query).await?;
        Ok(result.rows.into_iter().map(|r| serde_json::Value::Array(r)).collect())
    }
    
    pub async fn list_capabilities(&self) -> Result<Vec<serde_json::Value>> {
        let query = "MATCH (c:Capability) RETURN c.id, c.name, c.category, c.status ORDER BY c.category, c.name";
        let result = self.client.query(query).await?;
        Ok(result.rows.into_iter().map(|r| serde_json::Value::Array(r)).collect())
    }
}
