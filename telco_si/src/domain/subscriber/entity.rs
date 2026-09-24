use chrono::{DateTime, Utc};
use uuid::Uuid;

use crate::domain::events::DomainEvent;

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
    version: i64,
    events: Vec<DomainEvent>,
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
            version: 1,
            events: Vec::new(),
        }
    }

    pub fn suspend(&mut self) -> Result<(), SubscriberError> {
        match self.status {
            SubscriberStatus::Active => {
                self.status = SubscriberStatus::Suspended;
                self.updated_at = Utc::now();

                self.events.push(DomainEvent::SubscriberSuspended {
                    subscriber_id: self.id.value(),
                    occurred_at: self.updated_at,
                });

                Ok(())
            }

            SubscriberStatus::Suspended => Err(SubscriberError::AlreadySuspended),

            SubscriberStatus::Terminated => Err(SubscriberError::Terminated),
        }
    }

    pub fn activate(&mut self) -> Result<(), SubscriberError> {
        match self.status {
            SubscriberStatus::Suspended => {
                self.status = SubscriberStatus::Active;
                self.updated_at = Utc::now();

                self.events.push(DomainEvent::SubscriberActivated {
                    subscriber_id: self.id.value(),
                    occurred_at: self.updated_at,
                });

                Ok(())
            }

            SubscriberStatus::Active => Err(SubscriberError::AlreadyActive),

            SubscriberStatus::Terminated => Err(SubscriberError::Terminated),
        }
    }

    pub fn terminate(&mut self) -> Result<(), SubscriberError> {
        match self.status {
            SubscriberStatus::Active | SubscriberStatus::Suspended => {
                self.status = SubscriberStatus::Terminated;
                self.updated_at = Utc::now();

                self.events.push(DomainEvent::SubscriberTerminated {
                    subscriber_id: self.id.value(),
                    occurred_at: self.updated_at,
                });

                Ok(())
            }

            SubscriberStatus::Terminated => Err(SubscriberError::InvalidTermination),
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

    pub fn version(&self) -> i64 {
        self.version
    }

    pub fn increment_version(&mut self) {
        self.version += 1;
    }

    pub fn domain_events(&self) -> &[DomainEvent] {
        &self.events
    }

    pub fn clear_domain_events(&mut self) {
        self.events.clear();
    }

    pub fn take_domain_events(&mut self) -> Vec<DomainEvent> {
        std::mem::take(&mut self.events)
    }

    pub fn reconstitute(
        id: SubscriberId,
        account_number: AccountNumber,
        status: SubscriberStatus,
        balance: Money,
        plan_id: Option<Uuid>,
        created_at: DateTime<Utc>,
        updated_at: DateTime<Utc>,
        version: i64,
    ) -> Self {
        Self {
            id,
            account_number,
            status,
            balance,
            plan_id,
            created_at,
            updated_at,
            version,
            events: Vec::new(),
        }
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

    use crate::domain::events::DomainEvent;

    fn create_subscriber() -> Subscriber {
        let account_number = AccountNumber::new("ACC-10001").expect("valid account number");

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

        assert!(matches!(result, Err(SubscriberError::AlreadyActive)));
    }

    #[test]
    fn suspended_subscriber_cannot_be_suspended_again() {
        let mut subscriber = create_subscriber();

        subscriber.suspend().unwrap();

        let result = subscriber.suspend();

        assert!(matches!(result, Err(SubscriberError::AlreadySuspended)));
    }

    #[test]
    fn terminated_subscriber_cannot_be_activated() {
        let mut subscriber = create_subscriber();

        subscriber.terminate().unwrap();

        let result = subscriber.activate();

        assert!(matches!(result, Err(SubscriberError::Terminated)));
    }

    #[test]
    fn terminated_subscriber_cannot_be_suspended() {
        let mut subscriber = create_subscriber();

        subscriber.terminate().unwrap();

        let result = subscriber.suspend();

        assert!(matches!(result, Err(SubscriberError::Terminated)));
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

        assert!(matches!(result, Err(SubscriberError::InvalidTermination)));
    }

    #[test]
    fn suspending_subscriber_generates_event() {
        let account = AccountNumber::new("ACC-10001").unwrap();

        let mut subscriber = Subscriber::new(account);

        subscriber.suspend().unwrap();

        assert_eq!(subscriber.domain_events().len(), 1);

        assert!(matches!(
            subscriber.domain_events()[0],
            DomainEvent::SubscriberSuspended { .. }
        ));
    }

    #[test]
    fn invalid_suspend_does_not_generate_event() {
        let account = AccountNumber::new("ACC-10002").unwrap();

        let mut subscriber = Subscriber::new(account);

        subscriber.suspend().unwrap();

        let result = subscriber.suspend();

        assert!(result.is_err());

        assert_eq!(subscriber.domain_events().len(), 1);
    }
}
