use anyhow::{Context, Result};
use async_trait::async_trait;
use chrono::{DateTime, Utc};
use sqlx::SqlitePool;

use crate::{
    application::subscriber::repository::SubscriberRepository,
    domain::subscriber::{
        AccountNumber,
        Money,
        Subscriber,
        SubscriberId,
        SubscriberStatus,
    },
};

#[derive(Debug, sqlx::FromRow)]
struct SubscriberRow {
    id: String,
    account_number: String,
    status: String,
    balance_cents: i64,
    plan_id: Option<String>,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

impl SubscriberRow {
    fn into_domain(self) -> Result<Subscriber> {
        let id = uuid::Uuid::parse_str(&self.id)
            .context("invalid subscriber UUID in database")?;

        let subscriber_id = SubscriberId::from_uuid(id);

        let account_number =
            AccountNumber::new(self.account_number)
                .map_err(anyhow::Error::msg)?;

        let status = string_to_status(&self.status)?;

        let balance = Money::from_cents(self.balance_cents)
            .map_err(anyhow::Error::msg)?;

        let plan_id = self
            .plan_id
            .map(|value| uuid::Uuid::parse_str(&value))
            .transpose()
            .context("invalid plan UUID in database")?;

        Ok(Subscriber::reconstitute(
            subscriber_id,
            account_number,
            status,
            balance,
            plan_id,
            self.created_at,
            self.updated_at,
        ))
    }
}

pub struct SqliteSubscriberRepository {
    pool: SqlitePool,
}

impl SqliteSubscriberRepository {
    pub fn new(pool: SqlitePool) -> Self {
        Self { pool }
    }
}

#[async_trait]
impl SubscriberRepository for SqliteSubscriberRepository {
    async fn create(&self, subscriber: &Subscriber) -> Result<()> {
        sqlx::query(
            r#"
            INSERT INTO subscribers (
                id,
                account_number,
                status,
                balance_cents,
                plan_id,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            "#,
        )
        .bind(subscriber.id().value().to_string())
        .bind(subscriber.account_number().value())
        .bind(status_to_string(subscriber.status()))
        .bind(subscriber.balance().cents())
        .bind(subscriber.plan_id().map(|id| id.to_string()))
        .bind(subscriber.created_at())
        .bind(subscriber.updated_at())
        .execute(&self.pool)
        .await
        .context("failed to create subscriber")?;

        Ok(())
    }

    async fn find_by_id(
        &self,
        id: SubscriberId,
    ) -> Result<Option<Subscriber>> {
        let row = sqlx::query_as::<_, SubscriberRow>(
            r#"
            SELECT
                id,
                account_number,
                status,
                balance_cents,
                plan_id,
                created_at,
                updated_at
            FROM subscribers
            WHERE id = ?
            "#,
        )
        .bind(id.value().to_string())
        .fetch_optional(&self.pool)
        .await
        .context("failed to find subscriber")?;

        row.map(SubscriberRow::into_domain).transpose()
    }

    async fn find_by_account_number(
        &self,
        account_number: &str,
    ) -> Result<Option<Subscriber>> {
        let row = sqlx::query_as::<_, SubscriberRow>(
            r#"
            SELECT
                id,
                account_number,
                status,
                balance_cents,
                plan_id,
                created_at,
                updated_at
            FROM subscribers
            WHERE account_number = ?
            "#,
        )
        .bind(account_number)
        .fetch_optional(&self.pool)
        .await
        .context("failed to find subscriber by account number")?;

        row.map(SubscriberRow::into_domain).transpose()
    }

    async fn update(&self, subscriber: &Subscriber) -> Result<()> {
        sqlx::query(
            r#"
            UPDATE subscribers
            SET
                account_number = ?,
                status = ?,
                balance_cents = ?,
                plan_id = ?,
                updated_at = ?
            WHERE id = ?
            "#,
        )
        .bind(subscriber.account_number().value())
        .bind(status_to_string(subscriber.status()))
        .bind(subscriber.balance().cents())
        .bind(subscriber.plan_id().map(|id| id.to_string()))
        .bind(subscriber.updated_at())
        .bind(subscriber.id().value().to_string())
        .execute(&self.pool)
        .await
        .context("failed to update subscriber")?;

        Ok(())
    }
}

fn status_to_string(status: SubscriberStatus) -> &'static str {
    match status {
        SubscriberStatus::Active => "active",
        SubscriberStatus::Suspended => "suspended",
        SubscriberStatus::Terminated => "terminated",
    }
}

fn string_to_status(value: &str) -> Result<SubscriberStatus> {
    match value {
        "active" => Ok(SubscriberStatus::Active),
        "suspended" => Ok(SubscriberStatus::Suspended),
        "terminated" => Ok(SubscriberStatus::Terminated),
        _ => Err(anyhow::anyhow!(
            "invalid subscriber status: {value}"
        )),
    }
}