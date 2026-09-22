use thiserror::Error;

#[derive(Debug, Error)]
pub enum ApplicationError {
    #[error("subscriber not found")]
    SubscriberNotFound,

    #[error("account number already exists")]
    AccountNumberAlreadyExists,

    #[error("invalid request: {0}")]
    InvalidRequest(String),

    #[error("invalid subscriber state: {0}")]
    InvalidSubscriberState(String),

    #[error("infrastructure error: {0}")]
    Infrastructure(#[source] anyhow::Error),
}

pub type ApplicationResult<T> = Result<T, ApplicationError>;
