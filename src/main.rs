mod db;
mod models;

use anyhow::Result;
use clap::{Parser, Subcommand};
use db::Database;
use models::SiteIntent;

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
    }
    
    Ok(())
}
