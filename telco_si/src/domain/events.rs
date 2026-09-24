use chrono::{DateTime, Utc};
use uuid::Uuid;

#[derive(Debug, Clone)]
pub enum DomainEvent {
    SubscriberSuspended {
        subscriber_id: Uuid,
        occurred_at: DateTime<Utc>,
    },

    SubscriberActivated {
        subscriber_id: Uuid,
        occurred_at: DateTime<Utc>,
    },

    SubscriberTerminated {
        subscriber_id: Uuid,
        occurred_at: DateTime<Utc>,
    },
}
