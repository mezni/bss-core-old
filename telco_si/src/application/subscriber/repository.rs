use anyhow::Result;

use crate::domain::subscriber::{
    Subscriber,
    SubscriberId,
};

#[async_trait::async_trait]
pub trait SubscriberRepository: Send + Sync {
    async fn create(&self, subscriber: &Subscriber) -> Result<()>;

    async fn find_by_id(
        &self,
        id: SubscriberId,
    ) -> Result<Option<Subscriber>>;

    async fn find_by_account_number(
        &self,
        account_number: &str,
    ) -> Result<Option<Subscriber>>;

    async fn update(&self, subscriber: &Subscriber) -> Result<()>;
}