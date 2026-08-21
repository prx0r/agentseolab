// Free AI Models Integration
// Uses Cloudflare Workers AI and other free providers for testing

use anyhow::Result;
use reqwest::Client;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone)]
pub struct FreeAIConfig {
    pub cloudflare_account_id: String,
    pub cloudflare_api_token: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct InferenceRequest {
    pub model: String,
    pub messages: Vec<Message>,
    pub max_tokens: Option<u32>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Message {
    pub role: String,
    pub content: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct InferenceResponse {
    pub model: String,
    pub content: String,
    pub tokens_used: u32,
    pub provider: String,
}

pub struct FreeAI {
    config: FreeAIConfig,
    http: Client,
}

impl FreeAI {
    pub fn new(config: FreeAIConfig) -> Self {
        let http = Client::builder()
            .timeout(std::time::Duration::from_secs(30))
            .build()
            .unwrap();
        Self { config, http }
    }
    
    pub fn from_env() -> Self {
        Self::new(FreeAIConfig {
            cloudflare_account_id: std::env::var("CF_ACCOUNT_ID").unwrap_or_default(),
            cloudflare_api_token: std::env::var("CF_API_TOKEN").unwrap_or_default(),
        })
    }
    
    // Cloudflare Workers AI (free tier: 10,000 neurons/day)
    pub async fn cloudflare_inference(&self, model: &str, prompt: &str) -> Result<InferenceResponse> {
        let url = format!(
            "https://api.cloudflare.com/client/v4/accounts/{}/ai/run/{}",
            self.config.cloudflare_account_id, model
        );
        
        let response = self.http
            .post(&url)
            .header("Authorization", format!("Bearer {}", self.config.cloudflare_api_token))
            .json(&serde_json::json!({ "messages": [{ "role": "user", "content": prompt }] }))
            .send()
            .await?;
        
        let result: serde_json::Value = response.json().await?;
        
        Ok(InferenceResponse {
            model: model.to_string(),
            content: result["result"]["response"].as_str().unwrap_or("").to_string(),
            tokens_used: 0,
            provider: "cloudflare".to_string(),
        })
    }
    
    // List available free models
    pub async fn list_free_models(&self) -> Vec<FreeModel> {
        vec![
            FreeModel {
                id: "@cf/meta/llama-3.1-8b-instruct".to_string(),
                name: "Llama 3.1 8B Instruct".to_string(),
                provider: "cloudflare".to_string(),
                cost: 0.0,
                capabilities: vec!["text-generation".to_string(), "instruct".to_string()],
            },
            FreeModel {
                id: "@cf/mistral/mistral-7b-instruct-v0.1".to_string(),
                name: "Mistral 7B Instruct".to_string(),
                provider: "cloudflare".to_string(),
                cost: 0.0,
                capabilities: vec!["text-generation".to_string(), "instruct".to_string()],
            },
            FreeModel {
                id: "@cf/qwen/qwen1.5-0.5b-chat".to_string(),
                name: "Qwen 0.5B Chat".to_string(),
                provider: "cloudflare".to_string(),
                cost: 0.0,
                capabilities: vec!["text-generation".to_string(), "chat".to_string()],
            },
        ]
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FreeModel {
    pub id: String,
    pub name: String,
    pub provider: String,
    pub cost: f64,
    pub capabilities: Vec<String>,
}
