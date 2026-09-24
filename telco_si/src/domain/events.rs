use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
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

impl DomainEvent {
    pub fn event_type(&self) -> &'static str {
        match self {
            Self::SubscriberSuspended { .. } => "subscriber.suspended",
            Self::SubscriberActivated { .. } => "subscriber.activated",
            Self::SubscriberTerminated { .. } => "subscriber.terminated",
        }
    }

    pub fn aggregate_type(&self) -> &'static str {
        "subscriber"
    }

    pub fn aggregate_id(&self) -> Uuid {
        match self {
            Self::SubscriberSuspended { subscriber_id, .. }
            | Self::SubscriberActivated { subscriber_id, .. }
            | Self::SubscriberTerminated { subscriber_id, .. } => *subscriber_id,
        }
    }

    pub fn occurred_at(&self) -> DateTime<Utc> {
        match self {
            Self::SubscriberSuspended { occurred_at, .. }
            | Self::SubscriberActivated { occurred_at, .. }
            | Self::SubscriberTerminated { occurred_at, .. } => *occurred_at,
        }
    }
}
