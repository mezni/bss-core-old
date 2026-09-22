use actix_web::{HttpResponse, ResponseError};
use serde_json::json;

use crate::application::error::ApplicationError;

impl ResponseError for ApplicationError {
    fn error_response(&self) -> HttpResponse {
        match self {
            ApplicationError::SubscriberNotFound => HttpResponse::NotFound().json(json!({
                "error": self.to_string()
            })),

            ApplicationError::AccountNumberAlreadyExists => HttpResponse::Conflict().json(json!({
                "error": self.to_string()
            })),

            ApplicationError::InvalidRequest(_) => HttpResponse::BadRequest().json(json!({
                "error": self.to_string()
            })),

            ApplicationError::InvalidSubscriberState(_) => HttpResponse::Conflict().json(json!({
                "error": self.to_string()
            })),

            ApplicationError::Infrastructure(error) => {
                tracing::error!(
                    error = %error,
                    "infrastructure failure"
                );

                HttpResponse::InternalServerError().json(json!({
                    "error": "internal server error"
                }))
            }
        }
    }
}
