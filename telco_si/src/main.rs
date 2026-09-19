mod config;

use actix_web::{web, App, HttpResponse, HttpServer, Responder};
use anyhow::Result;
use config::AppConfig;
use tracing::info;
use tracing_subscriber::EnvFilter;

async fn health() -> impl Responder {
    info!("health check requested");

    HttpResponse::Ok().json(serde_json::json!({
        "status": "ok"
    }))
}

#[actix_web::main]
async fn main() -> Result<()> {
    tracing_subscriber::fmt()
        .with_env_filter(
            EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| EnvFilter::new("telco_si=info")),
        )
        .init();

    let config = AppConfig::from_env()?;

    info!(
        host = %config.host,
        port = config.port,
        "starting telco_si"
    );

    let bind_address = format!("{}:{}", config.host, config.port);

    HttpServer::new(|| {
        App::new()
            .route("/health", web::get().to(health))
    })
    .bind(&bind_address)?
    .run()
    .await?;

    Ok(())
}