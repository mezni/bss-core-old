use chrono::{DateTime, Utc};
use uuid::Uuid;

use super::{
    error::SubscriberError,
    value_objects::{AccountNumber, Money, SubscriberId, SubscriberStatus},
};

#[derive(Debug, Clone)]
pub struct Subscriber {
    id: SubscriberId,
    account_number: AccountNumber,
    status: SubscriberStatus,
    balance: Money,
    plan_id: Option<Uuid>,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

impl Subscriber {
    pub fn new(account_number: AccountNumber) -> Self {
        let now = Utc::now();

        Self {
            id: SubscriberId::new(),
            account_number,
            status: SubscriberStatus::Active,
            balance: Money::zero(),
            plan_id: None,
            created_at: now,
            updated_at: now,
        }
    }

    pub fn suspend(&mut self) -> Result<(), SubscriberError> {
        match self.status {
            SubscriberStatus::Active => {
                self.status = SubscriberStatus::Suspended;
                self.updated_at = Utc::now();

                Ok(())
            }

            SubscriberStatus::Suspended => {
                Err(SubscriberError::AlreadySuspended)
            }

            SubscriberStatus::Terminated => {
                Err(SubscriberError::Terminated)
            }
        }
    }

    pub fn activate(&mut self) -> Result<(), SubscriberError> {
        match self.status {
            SubscriberStatus::Suspended => {
                self.status = SubscriberStatus::Active;
                self.updated_at = Utc::now();

                Ok(())
            }

            SubscriberStatus::Active => {
                Err(SubscriberError::AlreadyActive)
            }

            SubscriberStatus::Terminated => {
                Err(SubscriberError::Terminated)
            }
        }
    }

    pub fn terminate(&mut self) -> Result<(), SubscriberError> {
        match self.status {
            SubscriberStatus::Active | SubscriberStatus::Suspended => {
                self.status = SubscriberStatus::Terminated;
                self.updated_at = Utc::now();

                Ok(())
            }

            SubscriberStatus::Terminated => {
                Err(SubscriberError::InvalidTermination)
            }
        }
    }

    pub fn id(&self) -> SubscriberId {
        self.id
    }

    pub fn account_number(&self) -> &AccountNumber {
        &self.account_number
    }

    pub fn status(&self) -> SubscriberStatus {
        self.status
    }

    pub fn balance(&self) -> Money {
        self.balance
    }

    pub fn plan_id(&self) -> Option<Uuid> {
        self.plan_id
    }

    pub fn created_at(&self) -> DateTime<Utc> {
        self.created_at
    }

    pub fn updated_at(&self) -> DateTime<Utc> {
        self.updated_at
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_subscriber() -> Subscriber {
        let account_number =
            AccountNumber::new("ACC-10001").expect("valid account number");

        Subscriber::new(account_number)
    }

    #[test]
    fn new_subscriber_is_active() {
        let subscriber = create_subscriber();

        assert_eq!(subscriber.status(), SubscriberStatus::Active);
        assert_eq!(subscriber.balance(), Money::zero());
    }

    #[test]
    fn subscriber_can_be_suspended() {
        let mut subscriber = create_subscriber();

        subscriber.suspend().unwrap();

        assert_eq!(subscriber.status(), SubscriberStatus::Suspended);
    }

    #[test]
    fn suspended_subscriber_can_be_activated() {
        let mut subscriber = create_subscriber();

        subscriber.suspend().unwrap();
        subscriber.activate().unwrap();

        assert_eq!(subscriber.status(), SubscriberStatus::Active);
    }

    #[test]
    fn active_subscriber_cannot_be_activated_again() {
        let mut subscriber = create_subscriber();

        let result = subscriber.activate();

        assert!(matches!(
            result,
            Err(SubscriberError::AlreadyActive)
        ));
    }

    #[test]
    fn suspended_subscriber_cannot_be_suspended_again() {
        let mut subscriber = create_subscriber();

        subscriber.suspend().unwrap();

        let result = subscriber.suspend();

        assert!(matches!(
            result,
            Err(SubscriberError::AlreadySuspended)
        ));
    }

    #[test]
    fn terminated_subscriber_cannot_be_activated() {
        let mut subscriber = create_subscriber();

        subscriber.terminate().unwrap();

        let result = subscriber.activate();

        assert!(matches!(
            result,
            Err(SubscriberError::Terminated)
        ));
    }

    #[test]
    fn terminated_subscriber_cannot_be_suspended() {
        let mut subscriber = create_subscriber();

        subscriber.terminate().unwrap();

        let result = subscriber.suspend();

        assert!(matches!(
            result,
            Err(SubscriberError::Terminated)
        ));
    }

    #[test]
    fn subscriber_can_be_terminated_from_active() {
        let mut subscriber = create_subscriber();

        subscriber.terminate().unwrap();

        assert_eq!(subscriber.status(), SubscriberStatus::Terminated);
    }

    #[test]
    fn subscriber_can_be_terminated_from_suspended() {
        let mut subscriber = create_subscriber();

        subscriber.suspend().unwrap();
        subscriber.terminate().unwrap();

        assert_eq!(subscriber.status(), SubscriberStatus::Terminated);
    }

    #[test]
    fn terminated_subscriber_cannot_be_terminated_again() {
        let mut subscriber = create_subscriber();

        subscriber.terminate().unwrap();

        let result = subscriber.terminate();

        assert!(matches!(
            result,
            Err(SubscriberError::InvalidTermination)
        ));
    }
}
