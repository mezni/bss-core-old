use actix_web::{
    web,
    HttpResponse,
    Responder,
};
use uuid::Uuid;

use crate::{
    application::subscriber::SubscriberService,
    infrastructure::persistence::subscriber_repository::SqliteSubscriberRepository,
};

use super::dto::{
    CreateSubscriberRequest,
    SubscriberResponse,
};

type SubscriberAppService =
    SubscriberService<SqliteSubscriberRepository>;

pub async fn create_subscriber(
    service: web::Data<SubscriberAppService>,
    request: web::Json<CreateSubscriberRequest>,
) -> impl Responder {
    match service
        .create(request.account_number.clone())
        .await
    {
        Ok(subscriber) => {
            HttpResponse::Created()
                .json(SubscriberResponse::from(subscriber))
        }

        Err(error) => {
            HttpResponse::BadRequest()
                .json(serde_json::json!({
                    "error": error.to_string()
                }))
        }
    }
}

pub async fn get_subscriber(
    service: web::Data<SubscriberAppService>,
    subscriber_id: web::Path<Uuid>,
) -> impl Responder {
    match service.get(subscriber_id.into_inner()).await {
        Ok(Some(subscriber)) => {
            HttpResponse::Ok()
                .json(SubscriberResponse::from(subscriber))
        }

        Ok(None) => {
            HttpResponse::NotFound()
                .json(serde_json::json!({
                    "error": "subscriber not found"
                }))
        }

        Err(error) => {
            HttpResponse::InternalServerError()
                .json(serde_json::json!({
                    "error": error.to_string()
                }))
        }
    }
}

pub async fn suspend_subscriber(
    service: web::Data<SubscriberAppService>,
    subscriber_id: web::Path<Uuid>,
) -> impl Responder {
    match service
        .suspend(subscriber_id.into_inner())
        .await
    {
        Ok(subscriber) => {
            HttpResponse::Ok()
                .json(SubscriberResponse::from(subscriber))
        }

        Err(error) => {
            HttpResponse::BadRequest()
                .json(serde_json::json!({
                    "error": error.to_string()
                }))
        }
    }
}

pub async fn activate_subscriber(
    service: web::Data<SubscriberAppService>,
    subscriber_id: web::Path<Uuid>,
) -> impl Responder {
    match service
        .activate(subscriber_id.into_inner())
        .await
    {
        Ok(subscriber) => {
            HttpResponse::Ok()
                .json(SubscriberResponse::from(subscriber))
        }

        Err(error) => {
            HttpResponse::BadRequest()
                .json(serde_json::json!({
                    "error": error.to_string()
                }))
        }
    }
}

pub async fn terminate_subscriber(
    service: web::Data<SubscriberAppService>,
    subscriber_id: web::Path<Uuid>,
) -> impl Responder {
    match service
        .terminate(subscriber_id.into_inner())
        .await
    {
        Ok(subscriber) => {
            HttpResponse::Ok()
                .json(SubscriberResponse::from(subscriber))
        }

        Err(error) => {
            HttpResponse::BadRequest()
                .json(serde_json::json!({
                    "error": error.to_string()
                }))
        }
    }
}

pub fn configure(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/subscribers")
            .route("", web::post().to(create_subscriber))
            .route("/{id}", web::get().to(get_subscriber))
            .route("/{id}/suspend", web::post().to(suspend_subscriber))
            .route("/{id}/activate", web::post().to(activate_subscriber))
            .route("/{id}/terminate", web::post().to(terminate_subscriber)),
    );
}