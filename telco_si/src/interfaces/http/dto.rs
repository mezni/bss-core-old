use serde::{Deserialize, Serialize};
use uuid::Uuid;
use validator::Validate;

use crate::domain::subscriber::{Subscriber, SubscriberStatus};

#[derive(Debug, Deserialize, Validate)]
pub struct CreateSubscriberRequest {
    #[validate(length(min = 3, max = 50))]
    pub account_number: String,
}

#[derive(Debug, Serialize, Deserialize)]
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
