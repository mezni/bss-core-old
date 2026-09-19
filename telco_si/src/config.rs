use anyhow::{Context, Result};
use std::env;

#[derive(Debug, Clone)]
pub struct AppConfig {
    pub host: String,
    pub port: u16,
    pub database_url: String,
}

impl AppConfig {
    pub fn from_env() -> Result<Self> {
        let host = env::var("APP_HOST").unwrap_or_else(|_| "127.0.0.1".to_string());

        let port = env::var("APP_PORT")
            .unwrap_or_else(|_| "8080".to_string())
            .parse::<u16>()
            .context("APP_PORT must be a valid port number")?;

        let database_url =
            env::var("DATABASE_URL").unwrap_or_else(|_| "sqlite://telco_si.db".to_string());

        Ok(Self {
            host,
            port,
            database_url,
        })
    }
}
