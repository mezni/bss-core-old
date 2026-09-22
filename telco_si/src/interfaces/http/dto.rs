use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::domain::subscriber::{Subscriber, SubscriberStatus};

#[derive(Debug, Deserialize)]
pub struct CreateSubscriberRequest {
    pub account_number: String,
}

#[derive(Debug, Serialize)]
pub struct SubscriberResponse {
    pub id: Uuid,
    pub account_number: String,
    pub status: SubscriberStatus,
    pub balance_cents: i64,
    pub plan_id: Option<Uuid>,
}

impl From<Subscriber> for SubscriberResponse {
    fn from(subscriber: Subscriber) -> Self {
        Self {
            id: subscriber.id().value(),
            account_number: subscriber.account_number().value().to_string(),
            status: subscriber.status(),
            balance_cents: subscriber.balance().cents(),
            plan_id: subscriber.plan_id(),
        }
    }
}
