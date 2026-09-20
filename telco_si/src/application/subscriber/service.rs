use anyhow::{anyhow, Context, Result};
use uuid::Uuid;

use crate::{
    application::subscriber::repository::SubscriberRepository,
    domain::subscriber::{
        AccountNumber,
        Subscriber,
        SubscriberId,
    },
};

#[derive(Clone)]
pub struct SubscriberService<R>
where
    R: SubscriberRepository,
{
    repository: R,
}

impl<R> SubscriberService<R>
where
    R: SubscriberRepository,
{
    pub fn new(repository: R) -> Self {
        Self { repository }
    }
}

impl<R> SubscriberService<R>
where
    R: SubscriberRepository,
{
    pub async fn create(
        &self,
        account_number: String,
    ) -> Result<Subscriber> {
        let account_number =
            AccountNumber::new(account_number)
                .map_err(anyhow::Error::msg)?;

        if self
            .repository
            .find_by_account_number(account_number.value())
            .await?
            .is_some()
        {
            return Err(anyhow!(
                "subscriber account number already exists"
            ));
        }

        let subscriber = Subscriber::new(account_number);

        self.repository
            .create(&subscriber)
            .await
            .context("failed to persist new subscriber")?;

        Ok(subscriber)
    }

    pub async fn get(
        &self,
        id: Uuid,
    ) -> Result<Option<Subscriber>> {
        let subscriber_id = SubscriberId::from_uuid(id);

        self.repository
            .find_by_id(subscriber_id)
            .await
            .context("failed to retrieve subscriber")
    }

    pub async fn suspend(
        &self,
        id: Uuid,
    ) -> Result<Subscriber> {
        let subscriber_id = SubscriberId::from_uuid(id);

        let mut subscriber = self
            .repository
            .find_by_id(subscriber_id)
            .await?
            .ok_or_else(|| anyhow!("subscriber not found"))?;

        subscriber
            .suspend()
            .map_err(anyhow::Error::msg)?;

        self.repository
            .update(&subscriber)
            .await
            .context("failed to persist suspended subscriber")?;

        Ok(subscriber)
    }

    pub async fn activate(
        &self,
        id: Uuid,
    ) -> Result<Subscriber> {
        let subscriber_id = SubscriberId::from_uuid(id);

        let mut subscriber = self
            .repository
            .find_by_id(subscriber_id)
            .await?
            .ok_or_else(|| anyhow!("subscriber not found"))?;

        subscriber
            .activate()
            .map_err(anyhow::Error::msg)?;

        self.repository
            .update(&subscriber)
            .await
            .context("failed to persist activated subscriber")?;

        Ok(subscriber)
    }

    pub async fn terminate(
        &self,
        id: Uuid,
    ) -> Result<Subscriber> {
        let subscriber_id = SubscriberId::from_uuid(id);

        let mut subscriber = self
            .repository
            .find_by_id(subscriber_id)
            .await?
            .ok_or_else(|| anyhow!("subscriber not found"))?;

        subscriber
            .terminate()
            .map_err(anyhow::Error::msg)?;

        self.repository
            .update(&subscriber)
            .await
            .context("failed to persist terminated subscriber")?;

        Ok(subscriber)
    }
}