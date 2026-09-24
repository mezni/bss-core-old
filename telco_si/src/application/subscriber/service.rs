use uuid::Uuid;

use crate::{
    application::{
        error::{ApplicationError, ApplicationResult},
        subscriber::{query::SubscriberPage, repository::SubscriberRepository},
    },
    domain::subscriber::{AccountNumber, Subscriber, SubscriberId},
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
    pub async fn create(&self, account_number: String) -> ApplicationResult<Subscriber> {
        let account_number = AccountNumber::new(account_number)
            .map_err(|error| ApplicationError::InvalidRequest(error.to_string()))?;

        if self
            .repository
            .find_by_account_number(account_number.value())
            .await
            .map_err(ApplicationError::Infrastructure)?
            .is_some()
        {
            return Err(ApplicationError::AccountNumberAlreadyExists);
        }

        let subscriber = Subscriber::new(account_number);

        self.repository
            .create(&subscriber)
            .await
            .map_err(ApplicationError::Infrastructure)?;

        Ok(subscriber)
    }

    pub async fn get(&self, id: Uuid) -> ApplicationResult<Option<Subscriber>> {
        let subscriber_id = SubscriberId::from_uuid(id);

        self.repository
            .find_by_id(subscriber_id)
            .await
            .map_err(ApplicationError::Infrastructure)
    }

    pub async fn suspend(&self, id: Uuid) -> ApplicationResult<Subscriber> {
        let subscriber_id = SubscriberId::from_uuid(id);

        let mut subscriber = self
            .repository
            .find_by_id(subscriber_id)
            .await
            .map_err(ApplicationError::Infrastructure)?
            .ok_or(ApplicationError::SubscriberNotFound)?;

        subscriber
            .suspend()
            .map_err(|error| ApplicationError::InvalidSubscriberState(error.to_string()))?;

        self.repository
            .update(&subscriber)
            .await
            .map_err(ApplicationError::Infrastructure)?;

        Ok(subscriber)
    }

    pub async fn activate(&self, id: Uuid) -> ApplicationResult<Subscriber> {
        let subscriber_id = SubscriberId::from_uuid(id);

        let mut subscriber = self
            .repository
            .find_by_id(subscriber_id)
            .await
            .map_err(ApplicationError::Infrastructure)?
            .ok_or(ApplicationError::SubscriberNotFound)?;

        subscriber
            .activate()
            .map_err(|error| ApplicationError::InvalidSubscriberState(error.to_string()))?;

        self.repository
            .update(&subscriber)
            .await
            .map_err(ApplicationError::Infrastructure)?;

        Ok(subscriber)
    }

    pub async fn terminate(&self, id: Uuid) -> ApplicationResult<Subscriber> {
        let subscriber_id = SubscriberId::from_uuid(id);

        let mut subscriber = self
            .repository
            .find_by_id(subscriber_id)
            .await
            .map_err(ApplicationError::Infrastructure)?
            .ok_or(ApplicationError::SubscriberNotFound)?;

        subscriber
            .terminate()
            .map_err(|error| ApplicationError::InvalidSubscriberState(error.to_string()))?;

        self.repository
            .update(&subscriber)
            .await
            .map_err(ApplicationError::Infrastructure)?;

        Ok(subscriber)
    }

    pub async fn list(&self, page: u32, page_size: u32) -> ApplicationResult<SubscriberPage> {
        if page == 0 {
            return Err(ApplicationError::InvalidRequest(
                "page must be greater than zero".to_string(),
            ));
        }

        if page_size == 0 || page_size > 100 {
            return Err(ApplicationError::InvalidRequest(
                "page_size must be between 1 and 100".to_string(),
            ));
        }

        let offset = (page - 1) * page_size;

        let (items, total) = self
            .repository
            .list(offset, page_size)
            .await
            .map_err(ApplicationError::Infrastructure)?;

        Ok(SubscriberPage {
            items,
            page,
            page_size,
            total,
        })
    }
}
