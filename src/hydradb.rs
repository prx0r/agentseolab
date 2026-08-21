use anyhow::Result;
use reqwest::Client;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone)]
pub struct HydraDBConfig {
    pub url: String,
    pub token: String,
    pub namespace: String,
    pub graph_id: String,
    pub cell_id: String,
}

impl Default for HydraDBConfig {
    fn default() -> Self {
        Self {
            url: std::env::var("HYDRA_URL").unwrap_or_else(|_| "http://127.0.0.1:8443".to_string()),
            token: std::env::var("HYDRA_TOKEN").unwrap_or_else(|_| "local-development-token-32-bytes".to_string()),
            namespace: std::env::var("HYDRA_NAMESPACE").unwrap_or_else(|_| "default".to_string()),
            graph_id: std::env::var("HYDRA_GRAPH_ID").unwrap_or_else(|_| "agentseolab".to_string()),
            cell_id: std::env::var("HYDRA_CELL_ID").unwrap_or_else(|_| "cell-0".to_string()),
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct QueryRequest {
    pub cell_id: String,
    pub query: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub params: Option<serde_json::Value>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct QueryResponse {
    pub columns: Vec<String>,
    pub rows: Vec<Vec<serde_json::Value>>,
    pub read_epoch: Option<u64>,
}

pub struct HydraDBClient {
    pub config: HydraDBConfig,
    http: Client,
}

impl HydraDBClient {
    pub fn new(config: HydraDBConfig) -> Self {
        let http = Client::builder()
            .timeout(std::time::Duration::from_secs(30))
            .build()
            .unwrap();
        Self { config, http }
    }
    
    pub fn from_env() -> Self {
        Self::new(HydraDBConfig::default())
    }
    
    pub async fn query(&self, cypher: &str) -> Result<QueryResponse> {
        let url = format!("{}/v1/graphs/{}/query", self.config.url, self.config.graph_id);
        
        let request = QueryRequest {
            cell_id: self.config.cell_id.clone(),
            query: cypher.to_string(),
            params: None,
        };
        
        let response = self.http
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.config.token))
            .header("X-Graph-Namespace", &self.config.namespace)
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await?;
        
        let status = response.status();
        let text = response.text().await?;
        
        if !status.is_success() {
            anyhow::bail!("HydraDB error {}: {}", status, text);
        }
        
        let result: QueryResponse = serde_json::from_str(&text)?;
        Ok(result)
    }
    
    pub async fn is_ready(&self) -> bool {
        let url = format!("{}/readyz", self.config.url.replace(":8443", ":9090"));
        match self.http.get(&url).send().await {
            Ok(resp) => resp.status().is_success(),
            Err(_) => false,
        }
    }
    
    pub async fn create_entity(&self, label: &str, id: &str, properties: &serde_json::Value) -> Result<()> {
        let props_json = serde_json::to_string(properties)?;
        let query = format!(
            "CREATE (n:{} {{id: '{}', {}}})",
            label,
            id,
            properties.as_object()
                .map(|m| m.iter().map(|(k, v)| format!("{}: {}", k, v)).collect::<Vec<_>>().join(", "))
                .unwrap_or_default()
        );
        self.query(&query).await?;
        Ok(())
    }
    
    pub async fn create_edge(&self, from_label: &str, from_id: &str, to_label: &str, to_id: &str, edge_type: &str) -> Result<()> {
        let query = format!(
            "MATCH (a:{} {{id: '{}'}}), (b:{} {{id: '{}'}}) CREATE (a)-[:{}]->(b)",
            from_label, from_id, to_label, to_id, edge_type
        );
        self.query(&query).await?;
        Ok(())
    }
    
    pub async fn find_entities(&self, label: &str) -> Result<Vec<serde_json::Value>> {
        let query = format!("MATCH (n:{}) RETURN n", label);
        let result = self.query(&query).await?;
        Ok(result.rows.into_iter().map(|r| r.into_iter().next().unwrap_or_default()).collect())
    }
}
