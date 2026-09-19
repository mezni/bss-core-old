use thiserror::Error;

#[derive(Debug, Error)]
pub enum SubscriberError {
    #[error("subscriber is already suspended")]
    AlreadySuspended,

    #[error("subscriber is already active")]
    AlreadyActive,

    #[error("subscriber is terminated")]
    Terminated,

    #[error("subscriber cannot be terminated from its current state")]
    InvalidTermination,

    #[error("balance cannot be negative")]
    NegativeBalance,

    #[error("invalid account number: {0}")]
    InvalidAccountNumber(String),
}
