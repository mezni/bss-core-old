mod application;
mod config;
mod database;
mod domain;
mod infrastructure;
mod interfaces;

use actix_web::{App, HttpResponse, HttpServer, Responder, web};
use anyhow::Result;
use application::subscriber::SubscriberService;
use config::AppConfig;
use database::create_pool;
use infrastructure::persistence::subscriber_repository::SqliteSubscriberRepository;
use interfaces::http::subscriber;
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
            EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("telco_si=info")),
        )
        .init();

    let config = AppConfig::from_env()?;

    info!(
        host = %config.host,
        port = config.port,
        database_url = %config.database_url,
        "starting telco_si"
    );

    let pool = create_pool(&config.database_url).await?;

    sqlx::migrate!("./migrations")
        .run(&pool)
        .await?;

    let database_check: (i64,) = sqlx::query_as("SELECT 1").fetch_one(&pool).await?;

    info!(result = database_check.0, "database connection verified");

    let subscriber_repository =
        SqliteSubscriberRepository::new(pool.clone());

    let subscriber_service =
        SubscriberService::new(subscriber_repository);

    let bind_address = format!("{}:{}", config.host, config.port);

    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(
                subscriber_service.clone(),
            ))
            .route("/health", web::get().to(health))
            .configure(subscriber::configure)
    })
    .bind(&bind_address)?
    .run()
    .await?;

    Ok(())
}