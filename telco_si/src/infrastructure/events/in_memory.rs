use anyhow::Result;
use async_trait::async_trait;
use std::sync::{Arc, Mutex};

use crate::{application::event_publisher::EventPublisher, domain::events::DomainEvent};

#[derive(Clone, Default)]
pub struct InMemoryEventPublisher {
    events: Arc<Mutex<Vec<DomainEvent>>>,
}

impl InMemoryEventPublisher {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn events(&self) -> Vec<DomainEvent> {
        self.events.lock().expect("event mutex poisoned").clone()
    }
}

#[async_trait]
impl EventPublisher for InMemoryEventPublisher {
    async fn publish(&self, event: DomainEvent) -> Result<()> {
        self.events
            .lock()
            .expect("event mutex poisoned")
            .push(event);

        Ok(())
    }
}
