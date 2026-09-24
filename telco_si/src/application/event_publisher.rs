use anyhow::Result;
use async_trait::async_trait;

use crate::domain::events::DomainEvent;

#[async_trait]
pub trait EventPublisher: Send + Sync {
    async fn publish(&self, event: DomainEvent) -> Result<()>;
}
