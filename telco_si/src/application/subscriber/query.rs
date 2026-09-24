use crate::domain::subscriber::SubscriberStatus;

#[derive(Debug, Clone)]
pub struct SubscriberListQuery {
    pub page: u32,
    pub page_size: u32,
    pub status: Option<SubscriberStatus>,
    pub account_number: Option<String>,
}

#[derive(Debug, Clone)]
pub struct SubscriberListItem {
    pub id: uuid::Uuid,
    pub account_number: String,
    pub status: String,
    pub balance_cents: i64,
}

#[derive(Debug, Clone)]
pub struct SubscriberPage {
    pub items: Vec<SubscriberListItem>,
    pub page: u32,
    pub page_size: u32,
    pub total: u64,
}
