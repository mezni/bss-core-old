use crate::{
    application::subscriber::SubscriberService,
    infrastructure::persistence::subscriber_repository::SqliteSubscriberRepository,
};

#[derive(Clone)]
pub struct AppState {
    pub subscriber_service: SubscriberService<SqliteSubscriberRepository>,
}

impl AppState {
    pub fn new(subscriber_service: SubscriberService<SqliteSubscriberRepository>) -> Self {
        Self { subscriber_service }
    }
}
