mod db;
mod models;
mod hydradb;
mod registry;
mod free_ai;

use anyhow::Result;
use clap::{Parser, Subcommand};
use db::Database;
use hydradb::{HydraDBClient, HydraDBConfig};
use models::SiteIntent;
use registry::CapabilityRegistry;
use free_ai::{FreeAI, FreeAIConfig};

#[derive(Parser)]
#[command(name = "agentseolab")]
#[command(about = "Domain Intelligence Lab — experiment infrastructure for agent preference testing")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Initialize database
    InitDb {
        /// Database path
        path: String,
    },
    
    /// Create a site intent from JSON file
    CreateIntent {
        /// Database path
        db: String,
        /// JSON file with intent data
        json: String,
    },
    
    /// Create an experiment from JSON file
    CreateExperiment {
        /// Database path
        db: String,
        /// JSON file with experiment data
        json: String,
    },
    
    /// Ingest an observation from JSON file
    IngestObservation {
        /// Database path
        db: String,
        /// JSON file with observation data
        json: String,
    },
    
    /// Generate report
    Report {
        /// Database path
        db: String,
    },
    
    /// HydraDB operations
    Hydra {
        #[command(subcommand)]
        command: HydraCommands,
    },
    
    /// Free AI models
    Ai {
        #[command(subcommand)]
        command: AiCommands,
    },
}

#[derive(Subcommand)]
enum HydraCommands {
    /// Check HydraDB connection
    Status,
    
    /// Create an entity in the graph
    CreateEntity {
        /// Entity label
        label: String,
        /// Entity ID
        id: String,
        /// Properties as JSON
        properties: String,
    },
    
    /// Create an edge between entities
    CreateEdge {
        /// Source entity label
        from_label: String,
        /// Source entity ID
        from_id: String,
        /// Target entity label
        to_label: String,
        /// Target entity ID
        to_id: String,
        /// Edge type
        edge_type: String,
    },
    
    /// Find all entities of a type
    FindEntities {
        /// Entity label
        label: String,
    },
    
    /// Run a custom OpenCypher query
    Query {
        /// OpenCypher query
        query: String,
    },
    
    /// Register a capability
    RegisterCapability {
        /// Capability ID
        id: String,
        /// Capability name
        name: String,
        /// Description
        description: String,
        /// Category
        category: String,
    },
}

#[derive(Subcommand)]
enum AiCommands {
    /// List available free models
    ListModels,
    
    /// Run inference with a free model
    Infer {
        /// Model ID
        model: String,
        /// Prompt
        prompt: String,
    },
}

fn load_json(path: &str) -> Result<serde_json::Value> {
    let content = std::fs::read_to_string(path)?;
    Ok(serde_json::from_str(&content)?)
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();
    
    match cli.command {
        Commands::InitDb { path } => {
            let _db = Database::connect(&path)?;
            println!("✓ Database initialized: {}", path);
        }
        
        Commands::CreateIntent { db, json } => {
            let db = Database::connect(&db)?;
            let data = load_json(&json)?;
            let intent: SiteIntent = serde_json::from_value(data)?;
            let id = db.insert_intent(&intent)?;
            println!("✓ Intent created: {}", id);
        }
        
        Commands::CreateExperiment { db, json } => {
            let db = Database::connect(&db)?;
            let data = load_json(&json)?;
            let intent_id = data["intent_id"].as_str().unwrap();
            let kind = data["kind"].as_str().unwrap();
            let hypothesis_id = data["hypothesis_id"].as_str();
            let preregistered = data["preregistered"].as_bool().unwrap_or(false);
            let id = db.insert_experiment(intent_id, kind, hypothesis_id, preregistered, &data)?;
            println!("✓ Experiment created: {}", id);
        }
        
        Commands::IngestObservation { db, json } => {
            let db = Database::connect(&db)?;
            let data = load_json(&json)?;
            let experiment_id = data["experiment_id"].as_str();
            let intent_id = data["intent_id"].as_str().unwrap();
            let evidence_tier = data["evidence_tier"].as_str().unwrap();
            let event_type = data["event_type"].as_str().unwrap();
            let model_family = data["model_family"].as_str();
            let model_version = data["model_version"].as_str();
            let provider = data["provider"].as_str();
            let session_id = data["session_id"].as_str();
            let id = db.insert_observation(experiment_id, intent_id, evidence_tier, event_type, model_family, model_version, provider, session_id, &data)?;
            println!("✓ Observation ingested: {}", id);
        }
        
        Commands::Report { db } => {
            let db = Database::connect(&db)?;
            println!("\n📊 Database Report\n");
            db.report()?;
        }
        
        Commands::Hydra { command } => {
            let client = HydraDBClient::from_env();
            
            match command {
                HydraCommands::Status => {
                    println!("🔍 Checking HydraDB connection...");
                    if client.is_ready().await {
                        println!("✓ HydraDB is ready");
                        println!("  URL: {}", client.config.url);
                        println!("  Namespace: {}", client.config.namespace);
                        println!("  Graph: {}", client.config.graph_id);
                    } else {
                        println!("✗ HydraDB is not reachable");
                        println!("  URL: {}", client.config.url);
                    }
                }
                
                HydraCommands::CreateEntity { label, id, properties } => {
                    let props: serde_json::Value = serde_json::from_str(&properties)?;
                    client.create_entity(&label, &id, &props).await?;
                    println!("✓ Entity created: {}:{}", label, id);
                }
                
                HydraCommands::CreateEdge { from_label, from_id, to_label, to_id, edge_type } => {
                    client.create_edge(&from_label, &from_id, &to_label, &to_id, &edge_type).await?;
                    println!("✓ Edge created: {}:{} -[{}]-> {}:{}", from_label, from_id, edge_type, to_label, to_id);
                }
                
                HydraCommands::FindEntities { label } => {
                    let entities = client.find_entities(&label).await?;
                    println!("\n📊 {} entities found:\n", entities.len());
                    for entity in &entities {
                        println!("  {:?}", entity);
                    }
                }
                
                HydraCommands::Query { query } => {
                    let result = client.query(&query).await?;
                    println!("\n📊 Query result:\n");
                    println!("  Columns: {:?}", result.columns);
                    println!("  Rows: {}", result.rows.len());
                    for row in &result.rows {
                        println!("    {:?}", row);
                    }
                }
                
                HydraCommands::RegisterCapability { id, name, description, category } => {
                    let registry = CapabilityRegistry::new(client);
                    let cap = registry::Capability {
                        id: id.clone(),
                        name,
                        description,
                        category,
                        status: "active".to_string(),
                        interfaces: vec!["mcp".to_string(), "rest".to_string()],
                        pricing: "free".to_string(),
                        performance: None,
                    };
                    registry.register_capability(&cap).await?;
                    println!("✓ Capability registered: {}", id);
                }
            }
        }
        
        Commands::Ai { command } => {
            let ai = FreeAI::from_env();
            
            match command {
                AiCommands::ListModels => {
                    let models = ai.list_free_models().await;
                    println!("\n📊 Free AI Models:\n");
                    for model in &models {
                        println!("  {} ({})", model.name, model.provider);
                        println!("    ID: {}", model.id);
                        println!("    Capabilities: {:?}", model.capabilities);
                        println!();
                    }
                }
                
                AiCommands::Infer { model, prompt } => {
                    println!("🔍 Running inference with {}...", model);
                    let response = ai.cloudflare_inference(&model, &prompt).await?;
                    println!("\n📊 Response:\n");
                    println!("  Model: {}", response.model);
                    println!("  Provider: {}", response.provider);
                    println!("  Content: {}", response.content);
                }
            }
        }
    }
    
    Ok(())
}
