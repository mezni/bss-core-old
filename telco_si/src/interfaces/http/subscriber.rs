use actix_web::{HttpResponse, Result, web};
use uuid::Uuid;
use validator::Validate;

use crate::application::{AppState, error::ApplicationError};

use super::dto::{
    CreateSubscriberRequest, SubscriberListQuery, SubscriberListResponse, SubscriberResponse,
};

pub async fn create_subscriber(
    state: web::Data<AppState>,
    request: web::Json<CreateSubscriberRequest>,
) -> Result<HttpResponse, ApplicationError> {
    request
        .validate()
        .map_err(|_| ApplicationError::Validation)?;

    let subscriber = state
        .subscriber_service
        .create(request.account_number.clone())
        .await?;

    Ok(HttpResponse::Created().json(SubscriberResponse::from(subscriber)))
}

pub async fn get_subscriber(
    state: web::Data<AppState>,
    subscriber_id: web::Path<Uuid>,
) -> Result<HttpResponse, ApplicationError> {
    match state
        .subscriber_service
        .get(subscriber_id.into_inner())
        .await?
    {
        Some(subscriber) => Ok(HttpResponse::Ok().json(SubscriberResponse::from(subscriber))),

        None => Err(ApplicationError::SubscriberNotFound),
    }
}

pub async fn suspend_subscriber(
    state: web::Data<AppState>,
    subscriber_id: web::Path<Uuid>,
) -> Result<HttpResponse, ApplicationError> {
    let subscriber = state
        .subscriber_service
        .suspend(subscriber_id.into_inner())
        .await?;

    Ok(HttpResponse::Ok().json(SubscriberResponse::from(subscriber)))
}

pub async fn activate_subscriber(
    state: web::Data<AppState>,
    subscriber_id: web::Path<Uuid>,
) -> Result<HttpResponse, ApplicationError> {
    let subscriber = state
        .subscriber_service
        .activate(subscriber_id.into_inner())
        .await?;

    Ok(HttpResponse::Ok().json(SubscriberResponse::from(subscriber)))
}

pub async fn terminate_subscriber(
    state: web::Data<AppState>,
    subscriber_id: web::Path<Uuid>,
) -> Result<HttpResponse, ApplicationError> {
    let subscriber = state
        .subscriber_service
        .terminate(subscriber_id.into_inner())
        .await?;

    Ok(HttpResponse::Ok().json(SubscriberResponse::from(subscriber)))
}

pub async fn list_subscribers(
    state: web::Data<AppState>,
    query: web::Query<SubscriberListQuery>,
) -> Result<HttpResponse, ApplicationError> {
    let page = query.page.unwrap_or(1);
    let page_size = query.page_size.unwrap_or(20);

    let result = state.subscriber_service.list(page, page_size).await?;

    let response = SubscriberListResponse {
        items: result.items.into_iter().map(Into::into).collect(),
        page: result.page,
        page_size: result.page_size,
        total: result.total,
    };

    Ok(HttpResponse::Ok().json(response))
}

pub fn configure(cfg: &mut web::ServiceConfig) {
    cfg.service(
        web::scope("/subscribers")
            .route("", web::get().to(list_subscribers))
            .route("", web::post().to(create_subscriber))
            .route("/{id}", web::get().to(get_subscriber))
            .route("/{id}/suspend", web::post().to(suspend_subscriber))
            .route("/{id}/activate", web::post().to(activate_subscriber))
            .route("/{id}/terminate", web::post().to(terminate_subscriber)),
    );
}
