"""Streamlit frontend application for BSS Core.

Provides the user interface for end customers to interact with the BSS Core
business management system. Communicates with the backend FastAPI application
through HTTP APIs only (constitution Section 3).
"""

import os
import sys
from pathlib import Path

import httpx
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.frontend.customer.api_client import CustomerAPIClient  # noqa: E402
from src.frontend.customer.form_page import (  # noqa: E402
    render_create_page,
    render_edit_page,
)
from src.frontend.customer.list_page import render_list_page  # noqa: E402

st.set_page_config(
    page_title="BSS Core - Business Management",
    page_icon="📦",
    layout="wide",
)


def _on_navigation_change() -> None:
    selection = st.session_state.get("navigation")
    st.session_state["customer_view"] = (
        "create" if selection == "New Customer" else "list"
    )


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


st.title("📦 BSS Core - Business Management System")
st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Customers", "New Customer", "Settings"],
    key="navigation",
    on_change=_on_navigation_change,
)

token = st.sidebar.text_input(
    "API token",
    type="password",
    value=st.session_state.get("bss_token", os.environ.get("BSS_API_TOKEN", "")),
)
st.session_state["bss_token"] = token
client = CustomerAPIClient(token=token)

if page == "Customers":
    if st.session_state.get("customer_view") == "edit":
        customer_id = st.session_state.get("edit_customer_id")
        if customer_id:
            if st.button("Back to list"):
                st.session_state["customer_view"] = "list"
                st.rerun()
            render_edit_page(client, customer_id)
        else:
            render_list_page(client)
    else:
        render_list_page(client)
elif page == "New Customer":
    if st.session_state.get("customer_view") == "edit":
        customer_id = st.session_state.get("edit_customer_id")
        if customer_id:
            if st.button("Back to list"):
                st.session_state["customer_view"] = "list"
                st.rerun()
            render_edit_page(client, customer_id)
        else:
            render_create_page(client)
    else:
        render_create_page(client)
elif page == "Settings":
    st.header("Settings")
    st.markdown(
        "Set `BSS_API_URL` to point the frontend at a non-default backend and "
        "`BSS_API_TOKEN` (or paste a token above) for authenticated calls."
    )
else:
    st.markdown("### Welcome to the BSS Core platform")
    st.header("System Status")
    check_backend_health()
    st.markdown(
        """
BSS Core is a modular business management system built with:
- **FastAPI** - Backend API
- **SQLite** - Initial database (designed for evolution)
- **Streamlit** - Frontend interface
- **Python 3.12+** - Runtime environment
"""
    )
    st.markdown("---")
    st.caption("BSS Core v0.1.0 | Modular Monolith Architecture")
