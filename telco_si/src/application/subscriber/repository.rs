use anyhow::Result;

use crate::{
    application::subscriber::query::{SubscriberListItem, SubscriberListQuery},
    domain::{
        events::DomainEvent,
        subscriber::{Subscriber, SubscriberId},
    },
};

#[async_trait::async_trait]
pub trait SubscriberRepository: Send + Sync {
    async fn create(&self, subscriber: &Subscriber) -> Result<()>;

    async fn find_by_id(&self, id: SubscriberId) -> Result<Option<Subscriber>>;

    async fn find_by_account_number(&self, account_number: &str) -> Result<Option<Subscriber>>;

    async fn save(&self, subscriber: &Subscriber, events: &[DomainEvent]) -> Result<()>;

    async fn list(&self, query: &SubscriberListQuery) -> Result<(Vec<SubscriberListItem>, u64)>;
}
