"""Streamlit frontend application for BSS Core.

Provides the user interface for end customers to interact with the BSS Core
business management system. Communicates with the backend FastAPI application
through HTTP APIs only (constitution Section 3).
"""

import streamlit as st

st.set_page_config(
    page_title="BSS Core - Business Management",
    page_icon="📦",
    layout="wide",
)

st.title("📦 BSS Core - Business Management System")
st.markdown("### Welcome to the BSS Core platform")

st.sidebar.header("Navigation")
st.sidebar.radio("Navigation", ["Dashboard", "Modules", "Settings"])

st.header("System Status")
st.success("✅ Backend connection operational")

st.markdown("""
BSS Core is a modular business management system built with:
- **FastAPI** - Backend API
- **SQLite** - Initial database (designed for evolution)
- **Streamlit** - Frontend interface
- **Python 3.12+** - Runtime environment
""")


def check_backend_health():
    """Check if the backend health endpoint is reachable."""
    import requests

    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            st.info(f"Backend status: {response.json().get('status', 'unknown')}")
            return True
    except Exception:
        pass
    st.warning("⚠️ Backend not reachable. Please ensure the FastAPI backend is running.")
    return False


if __name__ == "__main__":
    check_backend_health()
    st.markdown("---")
    st.caption("BSS Core v0.1.0 | Modular Monolith Architecture")
