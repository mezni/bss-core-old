"""Streamlit frontend application for BSS Core.

Provides the user interface for end customers to interact with the BSS Core
business management system. Communicates with the backend FastAPI application
through HTTP APIs only (constitution Section 3).
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import httpx
import streamlit as st

# Constants
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
METRICS_API = f"{API_BASE_URL}/api/v1/dashboard/metrics"

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.frontend.customer.api_client import CustomerAPIClient  # noqa: E402
from src.frontend.customer.form_page import (  # noqa: E402
    render_create_page,
    render_edit_page,
)
from src.frontend.customer.list_page import render_list_page  # noqa: E402
from src.frontend.streamlit_dashboard import (
    CATEGORIES,
    ROLE_TIERS,
    fetch_metrics,
    get_role_tier_from_token,
    render_refresh_control,
    render_role_indicator,
)

st.set_page_config(
    page_title="BSS Core - Business Management",
    page_icon="📦",
    layout="wide",
)


def _on_navigation_change() -> None:
    selection = st.session_state.get("navigation")
    st.session_state["customer_view"] = "create" if selection == "New Customer" else "list"


def check_backend_health() -> bool:
    """Check if the backend health endpoint is reachable."""
    try:
        response = httpx.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            st.info(f"Backend status: {response.json().get('status', 'unknown')}")
            return True
    except httpx.HTTPError:
        pass
    st.warning("⚠️ Backend not reachable. Please ensure the FastAPI backend is running.")
    return False


def render_dashboard_page() -> None:
    """Render the dashboard page with metric visualization."""
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
    rendered = False
    if metrics_data.get("metrics"):
        for metric in metrics_data["metrics"]:
            label = metric.get("metric_name", "Unknown")
            value = f"{metric.get('value', 0):.2f} {metric.get('unit', '')}"
            st.metric(label=label, value=value)
            rendered = True

    if not rendered:
        st.info("No metrics found matching the selected criteria.")

    # Role indicator and last refreshed
    render_role_indicator()

    last_refreshed = st.session_state.get("last_refresh", 0)
    if last_refreshed:
        refresh_time = datetime.fromtimestamp(last_refreshed).strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"Last refreshed: {refresh_time}")

    render_refresh_control()

    # Category tabs
    st.markdown("### Metrics by Category")
    for category in CATEGORIES:
        with st.expander(f"{category.title()} Metrics"):
            tab_metrics_data = fetch_metrics(
                category=category,
                role_tier=role_tier_value,
                period=period_value,
                start_date=start_date_obj,
                end_date=end_date_obj,
            )
            if tab_metrics_data.get("metrics"):
                for metric in tab_metrics_data["metrics"]:
                    label = metric.get("metric_name", "Unknown")
                    value = f"{metric.get('value', 0):.2f} {metric.get('unit', '')}"
                    st.caption(f"**{label}**: {value} {metric.get('unit', '')}")
            else:
                st.caption("No metrics found")


def render_customer_page() -> None:
    """Render the customer management page."""

    st.title("👥 Customer Management")
    st.markdown("Manage customer records and relationships.")

    token = st.sidebar.text_input(
        "API token",
        type="password",
        value=st.session_state.get("bss_token", os.environ.get("BSS_API_TOKEN", "")),
        help="Enter your JWT API token for authentication",
    )
    st.session_state["bss_token"] = token
    client = CustomerAPIClient(token=token)

    page = st.sidebar.radio(
        "Navigation",
        ["List", "New", "Edit"],
        key="customer_navigation",
    )

    if page == "List":
        render_list_page(client)
    elif page == "New":
        render_create_page(client)
    elif page == "Edit":
        customer_id = st.sidebar.text_input("Customer ID to edit")
        if customer_id:
            if st.button("Back to list"):
                st.session_state["customer_view"] = "list"
                st.rerun()
            render_edit_page(client, customer_id)
        else:
            render_list_page(client)


def render_new_customer_page() -> None:
    """Render the new customer creation page."""

    st.title("🆕 New Customer")
    st.markdown("Create a new customer record.")

    token = st.sidebar.text_input(
        "API token",
        type="password",
        value=st.session_state.get("bss_token", os.environ.get("BSS_API_TOKEN", "")),
    )
    st.session_state["bss_token"] = token
    client = CustomerAPIClient(token=token)

    render_create_page(client)


def render_settings_page() -> None:
    """Render the settings page."""
    st.title("⚙️ Settings")
    st.markdown(
        """
    Set `BSS_API_URL` to point the frontend at a non-default backend and
    `BSS_API_TOKEN` (or paste a token above) for authenticated calls.
    """
    )
    st.text_input("API URL", value="http://localhost:8000")
    st.text_input(
        "API Token",
        type="password",
        value=os.environ.get("BSS_API_TOKEN", ""),
    )
    st.caption("Configuration stored in session for this session only.")


def render() -> None:
    """Render the main application page based on navigation selection."""
    st.sidebar.title("BSS Core Navigation")
    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Customers", "New Customer", "Settings"],
        key="navigation",
        on_change=_on_navigation_change,
    )

    if page == "Dashboard":
        render_dashboard_page()
    elif page == "Customers":
        render_customer_page()
    elif page == "New Customer":
        render_new_customer_page()
    elif page == "Settings":
        render_settings_page()


if __name__ == "__main__":
    render()