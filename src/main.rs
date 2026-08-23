mod db;
mod models;
mod registry;

use anyhow::Result;
use clap::{Parser, Subcommand};
use db::Database;
use models::*;


#[derive(Parser)]
#[command(name = "agentseolab")]
#[command(about = "Domain Intelligence Lab — scientific experiment infrastructure for agent preference testing")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Initialize database with scientific schema
    InitDb {
        /// Database path
        path: String,
    },
    
    /// Capture immutable SiteIntent (MUST be before candidate generation)
    CaptureIntent {
        /// Database path
        db: String,
        /// JSON file with intent data
        json: String,
    },
    
    /// Record a field trial (actual agent search behavior)
    RecordFieldTrial {
        /// Database path
        db: String,
        /// JSON file with trial data
        json: String,
    },
    
    /// Record a pairwise comparison (preference measurement)
    RecordComparison {
        /// Database path
        db: String,
        /// JSON file with comparison data
        json: String,
    },
    
    /// Record an explanation (structured reason codes)
    RecordExplanation {
        /// Database path
        db: String,
        /// JSON file with explanation data
        json: String,
    },
    
    /// Add hypothesis to evidence library
    AddHypothesis {
        /// Database path
        db: String,
        /// JSON file with hypothesis data
        json: String,
    },
    
    /// Generate scientific report
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
        
        Commands::CaptureIntent { db, json } => {
            let db = Database::connect(&db)?;
            let data = load_json(&json)?;
            let intent: SiteIntent = serde_json::from_value(data)?;
            let record = intent.to_record();
            let id = db.insert_intent(&intent)?;
            println!("✓ SiteIntent captured: {}", id);
            println!("  Hash: {}", record.intent_hash);
            println!("  Purpose: {}", intent.purpose);
        }
        
        Commands::RecordFieldTrial { db, json } => {
            let db = Database::connect(&db)?;
            let data = load_json(&json)?;
            let trial: FieldTrial = serde_json::from_value(data)?;
            let id = db.insert_field_trial(&trial)?;
            println!("✓ Field trial recorded: {}", id);
            println!("  Agent: {} ({})", trial.agent_model, trial.provider);
            println!("  Queries: {}", trial.search_queries.len());
        }
        
        Commands::RecordComparison { db, json } => {
            let db = Database::connect(&db)?;
            let data = load_json(&json)?;
            let comp: PairwiseComparison = serde_json::from_value(data)?;
            let id = db.insert_pairwise_comparison(&comp)?;
            println!("✓ Pairwise comparison recorded: {}", id);
            println!("  {} vs {}", comp.candidate_a, comp.candidate_b);
            println!("  Chosen: {} (order: {})", comp.chosen, comp.ordering);
        }
        
        Commands::RecordExplanation { db, json } => {
            let db = Database::connect(&db)?;
            let data = load_json(&json)?;
            let explanation: Explanation = serde_json::from_value(data)?;
            let id = db.insert_explanation(&explanation)?;
            println!("✓ Explanation recorded: {}", id);
            println!("  Reason codes: {:?}", explanation.reason_codes);
        }
        
        Commands::AddHypothesis { db, json } => {
            let db = Database::connect(&db)?;
            let data = load_json(&json)?;
            let hyp: Hypothesis = serde_json::from_value(data)?;
            let id = db.insert_hypothesis(&hyp)?;
            println!("✓ Hypothesis added: {}", id);
            println!("  Statement: {}", hyp.statement);
            println!("  Status: {}", hyp.status);
        }
        
        Commands::Report { db } => {
            let db = Database::connect(&db)?;
            println!("\n📊 Scientific Report\n");
            db.report()?;
            println!("");
            db.report_pairwise_stats()?
        }
    }
    
    Ok(())
}
