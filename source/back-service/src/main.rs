mod core;
mod services;

use crate::core::db::Db;
use crate::core::logger::Logger;
use crate::core::errors::AppError;


#[tokio::main]
async fn main() -> Result<(), AppError> {
    // Initialize logger
    Logger::init();
    Logger::info("Starting application");

    // Create PostgreSQL pool
    let pool = Db::create_pool();

    Logger::info("Application finished");
    Ok(())
}
