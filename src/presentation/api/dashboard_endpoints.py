from __future__ import annotations

from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, status

from src.models.dashboard_metric import DashboardMetric
from src.models.reporting_period import ReportingPeriod
from src.services.dashboard_service import DashboardService
from src.infrastructure.db.config import get_db, init_db


# Create FastAPI app instance
app = FastAPI(title="BSS Core Dashboard API", version="0.1.0")

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(db_session_factory=lambda: db)


@router.get(
    "/metrics",
    summary="Retrieve dashboard metrics",
    description="Get aggregated operational metrics for the dashboard with filtering by category, role tier, period, and date range",
)
def get_dashboard_metrics(
    category: str | None = Query(
        None,
        description="Filter by metric category: customer, order, shipment, billing",
    ),
    role_tier: str | None = Query(
        None,
        description="Filter by required role tier: operator, manager, admin",
    ),
    period: str | None = Query(
        None,
        description="Predefined period: current_month, current_quarter, year_to_date",
    ),
    metric_name: str | None = Query(
        None,
        description="Filter by specific metric name",
    ),
    start_date: str | None = Query(
        None,
        description="ISO-8601 date filter start (e.g., '2026-01-01')",
    ),
    end_date: str | None = Query(
        None,
        description="ISO-8601 date filter end (e.g., '2026-11-11T23:59:59')",
    ),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=1000, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Retrieve dashboard metrics with filtering and pagination."""
    init_db()

    svc = get_dashboard_service(db)

    try:
        start_dt = (
            datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc)
            if start_date
            else None
        )
        end_dt = (
            datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc)
            if end_date
            else None
        )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ISO-8601 date format for start_date or end_date",
        )

    metrics = svc.get_metrics(
        category=category,
        role_tier=role_tier,
        period=period,
        metric_name=metric_name,
        start_date=start_dt,
        end_date=end_dt,
    )

    total = len(metrics)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_metrics = metrics[start_idx:end_idx]

    metrics_dict = []
    for m in page_metrics:
        metrics_dict.append(
            {
                "metric_name": m.metric_name,
                "value": float(m.value) if m.value is not None else 0.0,
                "unit": m.unit,
                "aggregation_type": m.aggregation_type,
                "date_range_start": m.date_range_start.isoformat()
                if m.date_range_start
                else None,
                "date_range_end": m.date_range_end.isoformat()
                if m.date_range_end
                else None,
                "reporting_period": m.reporting_period,
                "category": m.category,
                "category_specific_id": m.category_specific_id,
                "role_tier": m.role_tier,
                "last_refreshed": m.last_refreshed.isoformat()
                if m.last_refreshed
                else None,
                "created_at": m.created_at.isoformat()
                if m.created_at
                else None,
                "updated_at": m.updated_at.isoformat()
                if m.updated_at
                else None,
            }
        )

    return {
        "metrics": metrics_dict,
        "total": total,
        "page": page,
        "page_size": page_size,
        "last_refreshed": datetime.now(timezone.utc).isoformat(),
        "cache_ttl_seconds": 300,
    }


app.include_router(router)