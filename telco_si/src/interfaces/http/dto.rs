use serde::{Deserialize, Serialize};
use uuid::Uuid;
use validator::Validate;

use crate::{
    application::subscriber::SubscriberListItem,
    domain::subscriber::{Subscriber, SubscriberStatus},
};

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

#[derive(Debug, Serialize, Deserialize)]
pub struct SubscriberListItemResponse {
    pub id: Uuid,
    pub account_number: String,
    pub status: String,
    pub balance_cents: i64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SubscriberListResponse {
    pub items: Vec<SubscriberListItemResponse>,
    pub page: u32,
    pub page_size: u32,
    pub total: u64,
}

impl From<SubscriberListItem> for SubscriberListItemResponse {
    fn from(item: SubscriberListItem) -> Self {
        Self {
            id: item.id,
            account_number: item.account_number,
            status: item.status,
            balance_cents: item.balance_cents,
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct SubscriberListRequest {
    pub page: Option<u32>,
    pub page_size: Option<u32>,
    pub status: Option<String>,
    pub account_number: Option<String>,
}
