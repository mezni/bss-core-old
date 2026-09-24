use actix_web::{App, test, web};
use sqlx::{SqlitePool, sqlite::SqlitePoolOptions};

use telco_si::{
    application::{
        AppState,
        subscriber::{SubscriberListQuery, SubscriberService},
    },
    infrastructure::persistence::subscriber_repository::SqliteSubscriberRepository,
    interfaces::http::{
        dto::{SubscriberListResponse, SubscriberResponse},
        subscriber,
    },
};

async fn create_test_pool() -> SqlitePool {
    let pool = SqlitePoolOptions::new()
        .max_connections(1)
        .connect("sqlite::memory:")
        .await
        .expect("failed to create test database");

    sqlx::migrate!("./migrations")
        .run(&pool)
        .await
        .expect("failed to run migrations");

    pool
}

#[tokio::test]
async fn create_and_get_subscriber() {
    let pool = create_test_pool().await;

    let repository = SqliteSubscriberRepository::new(pool);
    let service = SubscriberService::new(repository);

    let subscriber = service
        .create("ACC-10001".to_string())
        .await
        .expect("subscriber creation failed");

    assert_eq!(subscriber.account_number().value(), "ACC-10001");

    assert_eq!(
        subscriber.status(),
        telco_si::domain::subscriber::SubscriberStatus::Active
    );

    let subscriber_id = subscriber.id().value();

    let loaded = service
        .get(subscriber_id)
        .await
        .expect("subscriber lookup failed")
        .expect("subscriber should exist");

    assert_eq!(loaded.id().value(), subscriber_id);

    assert_eq!(loaded.account_number().value(), "ACC-10001");
}

#[tokio::test]
async fn duplicate_account_number_is_rejected() {
    let pool = create_test_pool().await;

    let repository = SqliteSubscriberRepository::new(pool);
    let service = SubscriberService::new(repository);

    service
        .create("ACC-20001".to_string())
        .await
        .expect("first subscriber should be created");

    let result = service.create("ACC-20001".to_string()).await;

    assert!(matches!(
        result,
        Err(telco_si::application::error::ApplicationError::AccountNumberAlreadyExists)
    ));
}

#[tokio::test]
async fn subscriber_lifecycle_is_persisted() {
    let pool = create_test_pool().await;

    let repository = SqliteSubscriberRepository::new(pool);
    let service = SubscriberService::new(repository);

    let subscriber = service
        .create("ACC-30001".to_string())
        .await
        .expect("subscriber creation failed");

    let id = subscriber.id().value();

    let subscriber = service.suspend(id).await.expect("suspend failed");

    assert_eq!(
        subscriber.status(),
        telco_si::domain::subscriber::SubscriberStatus::Suspended
    );

    let subscriber = service.activate(id).await.expect("activate failed");

    assert_eq!(
        subscriber.status(),
        telco_si::domain::subscriber::SubscriberStatus::Active
    );

    let subscriber = service.terminate(id).await.expect("terminate failed");

    assert_eq!(
        subscriber.status(),
        telco_si::domain::subscriber::SubscriberStatus::Terminated
    );

    let loaded = service
        .get(id)
        .await
        .expect("lookup failed")
        .expect("subscriber should exist");

    assert_eq!(
        loaded.status(),
        telco_si::domain::subscriber::SubscriberStatus::Terminated
    );
}

#[actix_web::test]
async fn create_subscriber_through_http() {
    let pool = create_test_pool().await;

    let repository = SqliteSubscriberRepository::new(pool);
    let service = SubscriberService::new(repository);
    let state = AppState::new(service);

    let app = test::init_service(
        App::new()
            .app_data(web::Data::new(state))
            .configure(subscriber::configure),
    )
    .await;

    let request = test::TestRequest::post()
        .uri("/subscribers")
        .set_json(serde_json::json!({
            "account_number": "ACC-40001"
        }))
        .to_request();

    let response = test::call_service(&app, request).await;

    assert_eq!(response.status(), 201);

    let body: SubscriberResponse = test::read_body_json(response).await;

    assert_eq!(body.account_number, "ACC-40001");
    assert_eq!(body.balance_cents, 0);
}

#[actix_web::test]
async fn create_subscriber_rejects_invalid_account_number() {
    let pool = create_test_pool().await;

    let repository = SqliteSubscriberRepository::new(pool);
    let service = SubscriberService::new(repository);
    let state = AppState::new(service);

    let app = test::init_service(
        App::new()
            .app_data(web::Data::new(state))
            .configure(subscriber::configure),
    )
    .await;

    let request = test::TestRequest::post()
        .uri("/subscribers")
        .set_json(serde_json::json!({
            "account_number": "AB"
        }))
        .to_request();

    let response = test::call_service(&app, request).await;

    assert_eq!(response.status(), 400);
}

#[actix_web::test]
async fn list_subscribers_returns_paginated_results() {
    let pool = create_test_pool().await;

    let repository = SqliteSubscriberRepository::new(pool);
    let service = SubscriberService::new(repository);

    service.create("ACC-50001".to_string()).await.unwrap();

    service.create("ACC-50002".to_string()).await.unwrap();

    let state = AppState::new(service);

    let app = test::init_service(
        App::new()
            .app_data(web::Data::new(state))
            .configure(subscriber::configure),
    )
    .await;

    let request = test::TestRequest::get()
        .uri("/subscribers?page=1&page_size=10")
        .to_request();

    let response = test::call_service(&app, request).await;

    assert_eq!(response.status(), 200);

    let body: SubscriberListResponse = test::read_body_json(response).await;

    assert_eq!(body.page, 1);
    assert_eq!(body.page_size, 10);
    assert_eq!(body.total, 2);
    assert_eq!(body.items.len(), 2);
}

#[tokio::test]
async fn subscriber_pagination_returns_correct_page() {
    let pool = create_test_pool().await;

    let repository = SqliteSubscriberRepository::new(pool);
    let service = SubscriberService::new(repository);

    for account in ["ACC-60001", "ACC-60002", "ACC-60003"] {
        service.create(account.to_string()).await.unwrap();
    }

    let result = service
        .list(SubscriberListQuery {
            page: 2,
            page_size: 2,
            status: None,
            account_number: None,
        })
        .await
        .unwrap();

    assert_eq!(result.page, 2);
    assert_eq!(result.page_size, 2);
    assert_eq!(result.total, 3);
    assert_eq!(result.items.len(), 1);
}

#[actix_web::test]
async fn list_subscribers_can_filter_by_status() {
    let pool = create_test_pool().await;

    let repository = SqliteSubscriberRepository::new(pool);
    let service = SubscriberService::new(repository);

    let first = service.create("ACC-70001".to_string()).await.unwrap();

    service.suspend(first.id().value()).await.unwrap();

    service.create("ACC-70002".to_string()).await.unwrap();

    let state = AppState::new(service);

    let app = test::init_service(
        App::new()
            .app_data(web::Data::new(state))
            .configure(subscriber::configure),
    )
    .await;

    let request = test::TestRequest::get()
        .uri("/subscribers?status=suspended")
        .to_request();

    let response = test::call_service(&app, request).await;

    assert_eq!(response.status(), 200);

    let body: SubscriberListResponse = test::read_body_json(response).await;

    assert_eq!(body.total, 1);
    assert_eq!(body.items[0].account_number, "ACC-70001");
}

#[actix_web::test]
async fn list_subscribers_can_filter_by_account_number() {
    let pool = create_test_pool().await;

    let repository = SqliteSubscriberRepository::new(pool);
    let service = SubscriberService::new(repository);

    service.create("ACC-80001".to_string()).await.unwrap();

    service.create("ACC-80002".to_string()).await.unwrap();

    let state = AppState::new(service);

    let app = test::init_service(
        App::new()
            .app_data(web::Data::new(state))
            .configure(subscriber::configure),
    )
    .await;

    let request = test::TestRequest::get()
        .uri("/subscribers?account_number=ACC-80002")
        .to_request();

    let response = test::call_service(&app, request).await;

    assert_eq!(response.status(), 200);

    let body: SubscriberListResponse = test::read_body_json(response).await;

    assert_eq!(body.total, 1);
    assert_eq!(body.items[0].account_number, "ACC-80002");
}

#[actix_web::test]
async fn list_subscribers_rejects_invalid_status() {
    let pool = create_test_pool().await;

    let repository = SqliteSubscriberRepository::new(pool);
    let service = SubscriberService::new(repository);

    let state = AppState::new(service);

    let app = test::init_service(
        App::new()
            .app_data(web::Data::new(state))
            .configure(subscriber::configure),
    )
    .await;

    let request = test::TestRequest::get()
        .uri("/subscribers?status=unknown")
        .to_request();

    let response = test::call_service(&app, request).await;

    assert_eq!(response.status(), 400);
}
