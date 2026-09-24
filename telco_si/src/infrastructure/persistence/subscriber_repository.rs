use anyhow::{Context, Result};
use async_trait::async_trait;
use chrono::{DateTime, Utc};
use sqlx::{QueryBuilder, SqlitePool};

use crate::{
    application::subscriber::{
        query::{SubscriberListItem, SubscriberListQuery},
        repository::SubscriberRepository,
    },
    domain::subscriber::{AccountNumber, Money, Subscriber, SubscriberId, SubscriberStatus},
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
        let id = uuid::Uuid::parse_str(&self.id).context("invalid subscriber UUID in database")?;

        let subscriber_id = SubscriberId::from_uuid(id);

        let account_number = AccountNumber::new(self.account_number).map_err(anyhow::Error::msg)?;

        let status = string_to_status(&self.status)?;

        let balance = Money::from_cents(self.balance_cents).map_err(anyhow::Error::msg)?;

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

#[derive(Debug, sqlx::FromRow)]
struct SubscriberListRow {
    id: String,
    account_number: String,
    status: String,
    balance_cents: i64,
}

#[derive(Clone)]
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

    async fn find_by_id(&self, id: SubscriberId) -> Result<Option<Subscriber>> {
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

    async fn find_by_account_number(&self, account_number: &str) -> Result<Option<Subscriber>> {
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

    async fn list(&self, query: &SubscriberListQuery) -> Result<(Vec<SubscriberListItem>, u64)> {
        let offset = (query.page - 1) * query.page_size;

        let mut builder = QueryBuilder::<sqlx::Sqlite>::new(
            r#"
            SELECT
                id,
                account_number,
                status,
                balance_cents
            FROM subscribers
            WHERE 1 = 1
            "#,
        );

        if let Some(status) = query.status {
            builder.push(" AND status = ");
            builder.push_bind(status_to_string(status));
        }

        if let Some(account_number) = query.account_number.as_deref() {
            builder.push(" AND account_number = ");
            builder.push_bind(account_number);
        }

        builder.push(" ORDER BY created_at DESC ");

        builder.push(" LIMIT ");
        builder.push_bind(query.page_size);

        builder.push(" OFFSET ");
        builder.push_bind(offset);

        let rows: Vec<SubscriberListRow> = builder
            .build_query_as()
            .fetch_all(&self.pool)
            .await
            .context("failed to list subscribers")?;

        let mut count_builder =
            QueryBuilder::<sqlx::Sqlite>::new("SELECT COUNT(*) FROM subscribers WHERE 1 = 1");

        if let Some(status) = query.status {
            count_builder.push(" AND status = ");
            count_builder.push_bind(status_to_string(status));
        }

        if let Some(account_number) = query.account_number.as_deref() {
            count_builder.push(" AND account_number = ");
            count_builder.push_bind(account_number);
        }

        let total: (i64,) = count_builder
            .build_query_as()
            .fetch_one(&self.pool)
            .await
            .context("failed to count subscribers")?;

        let items = rows
            .into_iter()
            .map(|row| SubscriberListItem {
                id: uuid::Uuid::parse_str(&row.id).expect("invalid subscriber UUID"),
                account_number: row.account_number,
                status: row.status,
                balance_cents: row.balance_cents,
            })
            .collect();

        Ok((items, total.0 as u64))
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
        _ => Err(anyhow::anyhow!("invalid subscriber status: {value}")),
    }
}
