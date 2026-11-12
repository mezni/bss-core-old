from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import (
    or_,
    select,
)

from src.models.dashboard_metric import DashboardMetric


class DashboardService:
    """Service layer for dashboard metric operations."""

    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    def _get_session(self):
        from src.domain.database import get_session

        return self.db_session_factory() if callable(self.db_session_factory) else get_session()

    def get_metrics(
        self,
        *,
        category: str | None = None,
        role_tier: str | None = None,
        period: str | None = None,
        metric_name: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ):
        """Get dashboard metrics with optional filtering."""
        session = self._get_session()

        query = select(DashboardMetric)

        if category:
            query = query.where(DashboardMetric.category == category)

        if role_tier:
            query = query.where(DashboardMetric.role_tier == role_tier)

        if period:
            query = query.where(DashboardMetric.reporting_period == period)

        if metric_name:
            query = query.where(DashboardMetric.metric_name == metric_name)

        if start_date:
            query = query.where(DashboardMetric.date_range_start >= start_date)

        if end_date:
            query = query.where(DashboardMetric.date_range_end <= end_date)

        result = session.execute(query.order_by(DashboardMetric.metric_name))
        return result.scalars().unique().all()

    def get_metrics_by_category(
        self,
        category: str,
        role_tier: str | None = None,
    ):
        """Get metrics for a specific category with role filtering."""
        session = self._get_session()

        query = select(DashboardMetric).where(DashboardMetric.category == category)

        if role_tier:
            query = query.where(
                or_(
                    DashboardMetric.role_tier == role_tier,
                    DashboardMetric.role_tier.is_(None),
                )
            )

        result = session.execute(query.order_by(DashboardMetric.metric_name))
        return result.scalars().unique().all()

    def get_billing_metrics(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ):
        """Get billing-specific metrics filtered by date range."""
        session = self._get_session()

        query = select(DashboardMetric).where(DashboardMetric.category == "billing")

        if start_date:
            query = query.where(DashboardMetric.date_range_start >= start_date)

        if end_date:
            query = query.where(DashboardMetric.date_range_end <= end_date)

        result = session.execute(query.order_by(DashboardMetric.metric_name))
        return result.scalars().unique().all()

    def get_recent_metrics(
        self,
        hours: int = 24,
        category: str | None = None,
    ):
        """Get metrics refreshed within the last N hours."""
        session = self._get_session()

        since = datetime.now(UTC) - timedelta(hours=hours)

        query = select(DashboardMetric).where(
            DashboardMetric.last_refreshed >= since
        )

        if category:
            query = query.where(DashboardMetric.category == category)

        result = session.execute(query.order_by(DashboardMetric.metric_name))
        return result.scalars().unique().all()

    def refresh_metrics(self):
        """Trigger metric refresh (placeholder for background task integration)."""
        # This would be called by the APScheduler/Celery beat task
        # to recalculate and update all dashboard metrics
        session = self._get_session()
        # Update last_refreshed timestamp for all metrics
        from sqlalchemy import update as sa_update
        session.execute(
            sa_update(DashboardMetric)
            .values(last_refreshed=datetime.now(UTC))
            .where(True)
        )
        session.commit()

    def get_categories(self):
        """Get distinct metric categories."""
        session = self._get_session()
        from sqlalchemy import distinct, select
        result = session.execute(select(distinct(DashboardMetric.category)))
        return [row[0] for row in result.fetchall()]

    def get_role_tiers(self):
        """Get distinct role tiers."""
        session = self._get_session()
        from sqlalchemy import distinct, select
        result = session.execute(
            select(distinct(DashboardMetric.role_tier).where(DashboardMetric.role_tier.isnot(None)))
        )
        return [row[0] for row in result.fetchall()]