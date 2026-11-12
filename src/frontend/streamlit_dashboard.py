"""Streamlit dashboard UI for operational data visualization and metric exploration.

Provides an interactive web interface for viewing aggregated business metrics
with date filtering, role-based access, and chart visualizations.
"""

from __future__ import annotations

import json
import os
import time
from datetime import date, datetime

import httpx
import streamlit as st

# Constants
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
METRICS_API = f"{API_BASE_URL}/api/v1/dashboard/metrics"

ROLE_TIERS = ["operator", "manager", "admin"]
CATEGORIES = ["customer", "order", "shipment", "billing"]

# Page config
st.set_page_config(
    page_title="BSS Core - Dashboard",
    page_icon="📊",
    layout="wide",
)

# Session state initialization
if "token" not in st.session_state:
    st.session_state["token"] = ""
if "role_tier" not in st.session_state:
    st.session_state["role_tier"] = "operator"
if "metrics_cache" not in st.session_state:
    st.session_state["metrics_cache"] = {}
if "last_refresh" not in st.session_state:
    st.session_state["last_refresh"] = 0
if "refresh_interval" not in st.session_state:
    st.session_state["refresh_interval"] = 300  # 5 minutes in seconds


def set_token(token: str) -> None:
    """Set the authentication token and refresh metrics."""
    st.session_state["token"] = token
    st.session_state["role_tier"] = "operator"  # default, will be updated from token


def get_role_tier_from_token(token: str) -> str:
    """Extract role tier from JWT token."""
    if not token:
        return "operator"
    try:
        # Decode JWT without verification to get role claim
        # In production, use proper JWT validation
        parts = token.split(".")
        if len(parts) >= 2:
            import base64
            payload = parts[1]
            # Add padding if needed
            missing_padding = 4 - len(payload) % 4
            if missing_padding != 4:
                payload += "=" * missing_padding
            decoded = base64.urlsafe_b64decode(payload).decode("utf-8")
            payload_data = json.loads(decoded)
            return payload_data.get("role_tier", "operator")
    except Exception:
        pass
    return "operator"


def fetch_metrics(
    category: str | None = None,
    role_tier: str | None = None,
    period: str | None = None,
    metric_name: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    force_refresh: bool = False,
) -> dict:
    """Fetch dashboard metrics from the API."""
    params = {}
    if category:
        params["category"] = category
    if role_tier:
        params["role_tier"] = role_tier
    if period:
        params["period"] = period
    if metric_name:
        params["metric_name"] = metric_name
    if start_date:
        params["start_date"] = start_date.isoformat()
    if end_date:
        params["end_date"] = end_date.isoformat()

    headers = {}
    if st.session_state.get("token"):
        headers["Authorization"] = f"Bearer {st.session_state['token']}"

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(METRICS_API, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                # Update cache and refresh time
                st.session_state["metrics_cache"] = data
                st.session_state["last_refresh"] = time.time()
                return data
            elif response.status_code == 403:
                st.error("❌ Access denied. Insufficient permissions for requested metrics.")
                return {"metrics": [], "total": 0, "page": 1, "page_size": 50}
            else:
                st.error(f"❌ API error: {response.status_code} - {response.text}")
                return {"metrics": [], "total": 0, "page": 1, "page_size": 50}
    except httpx.RequestError as e:
        st.error(f"❌ Connection error: {str(e)}")
        return {"metrics": [], "total": 0, "page": 1, "page_size": 50}


def render_role_indicator() -> None:
    """Render the user's role tier badge."""
    role = st.session_state.get("role_tier", "operator")
    role_colors = {
        "operator": "🟢",
        "manager": "🟡",
        "admin": "🔴",
    }
    role_descriptions = {
        "operator": "Operator - Order, shipment, recent invoices",
        "manager": "Manager - All operator metrics + billing, revenue summaries",
        "admin": "Admin - All metrics including sensitive financial data",
    }
    color = role_colors.get(role, "⚪")
    st.sidebar.markdown(f"**Role:** {color} {role.title()}")
    st.sidebar.caption(role_descriptions.get(role, ""))


def render_refresh_control() -> None:
    """Render the manual refresh control."""
    if st.sidebar.button("🔄 Refresh Now", use_container_width=True):
        # Force refresh by clearing cache timestamp
        st.session_state["last_refresh"] = 0
        st.rerun()

    # auto-refresh indicator
    time_since_refresh = time.time() - st.session_state.get("last_refresh", 0)
    minutes_since = int(time_since_refresh / 60)
    if minutes_since < 1:
        st.sidebar.caption(f"✓ Data refreshed {minutes_since} minute ago")
    else:
        st.sidebar.caption(f"✓ Data refreshed {minutes_since} minutes ago")


def render_metric_widgets(metrics: list) -> None:
    """Render individual metric widgets."""
    if not metrics:
        st.info("No metrics found matching the selected criteria.")
        return

    st.markdown("### Metric Summary")
    cols = st.columns(min(len(metrics), 4))
    for i, metric in enumerate(metrics):
        with cols[i % 4]:
            st.metric(
                label=metric.get("metric_name", "Unknown"),
                value=f"{metric.get('value', 0):.2f} {metric.get('unit', '')}",
                delta=None,
            )


def render() -> None:
    """Render the full dashboard UI."""
    # Header
    st.title("📊 BSS Core Dashboard")
    st.markdown("**Operational visibility across business modules**")

    # Token authentication
    with st.sidebar:
        st.header("Authentication")
        token = st.text_input(
            "API Token",
            type="password",
            value=st.session_state.get("token", ""),
            help="Enter your JWT API token for authentication",
        )
        st.session_state["token"] = token

        if token:
            role = get_role_tier_from_token(token)
            st.session_state["role_tier"] = role
            render_role_indicator()

    # Query parameters
    with st.sidebar:
        st.header("Filters")
        
        # Category filter
        category = st.selectbox(
            "Category",
            ["All"] + CATEGORIES,
            index=0,
            help="Filter metrics by business category",
        )
        category_value = None if category == "All" else category

        # Period filter
        period = st.selectbox(
            "Period",
            ["All", "current_month", "current_quarter", "year_to_date"],
            index=0,
            help="Predefined reporting period",
        )
        period_value = None if period == "All" else period

        # Role tier (readonly, derived from token)
        role_tier = st.selectbox(
            "Role Tier",
            ["All"] + ROLE_TIERS,
            index=ROLE_TIERS.index(st.session_state.get("role_tier", "operator")) 
            if st.session_state.get("role_tier") in ROLE_TIERS else 0,
            help="Filter metrics by role-based visibility (readonly)",
            disabled=bool(token),
        )
        role_tier_value = None if role_tier == "All" else role_tier

        # Date range
        st.markdown("**Date Range**")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start", value=None)
        with col2:
            end_date = st.date_input("End", value=None)

        # Refresh control
        render_refresh_control()

    # Fetch metrics
    start_date_obj = None
    end_date_obj = None
    if start_date:
        start_date_obj = datetime(start_date.year, start_date.month, start_date.day)
    if end_date:
        end_date_obj = datetime(end_date.year, end_date.month, end_date.day)

    with st.spinner("Fetching metrics..."):
        metrics_data = fetch_metrics(
            category=category_value,
            role_tier=role_tier_value,
            period=period_value,
            start_date=start_date_obj,
            end_date=end_date_obj,
        )

    # Display metrics
    st.markdown("### Metric Summary Bar")
    render_metric_widgets(metrics_data.get("metrics", []))

    # Category tabs
    tabs = st.tabs(CATEGORIES + ["All"])
    for _, tab in zip(CATEGORIES + ["All"], tabs, strict=True):
        with tab:
            filtered_category = category_value if category_value else None
            tab_metrics_data = fetch_metrics(
                category=filtered_category,
                role_tier=role_tier_value,
                period=period_value,
                start_date=start_date_obj,
                end_date=end_date_obj,
            )
            render_metric_widgets(tab_metrics_data.get("metrics", []))

    # Role indicator and last refreshed
    render_role_indicator()
    
    last_refreshed = st.session_state.get("last_refresh", 0)
    if last_refreshed:
        refresh_time = datetime.fromtimestamp(last_refreshed).strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"Last refreshed: {refresh_time}")
    
    render_refresh_control()


if __name__ == "__main__":
    render()