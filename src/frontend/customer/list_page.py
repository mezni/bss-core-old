"""Customer list, search, and filter page."""

from __future__ import annotations

import streamlit as st

from .api_client import CustomerAPIClient, CustomerAPIError

TYPE_OPTIONS = ["", "INDIVIDUAL", "BUSINESS"]
STATUS_OPTIONS = ["", "ACTIVE", "INACTIVE"]


def _label(value: str) -> str:
    return value.title() if value else "All"


def _show_error(error: CustomerAPIError) -> None:
    st.error(f"{error.code}: {error.message}")


def render_list_page(client: CustomerAPIClient) -> None:
    """Render searchable, filterable, paginated customer results."""
    st.header("Customers")

    if st.button("New customer", type="primary"):
        st.session_state["customer_view"] = "create"
        st.rerun()

    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    q = col1.text_input("Search", key="customer_q", placeholder="Name, email, registration")
    customer_type = col2.selectbox(
        "Type", TYPE_OPTIONS, format_func=_label, key="customer_type_filter"
    )
    status = col3.selectbox(
        "Status", STATUS_OPTIONS, format_func=_label, key="customer_status_filter"
    )
    page_size = col4.number_input(
        "Page size", min_value=1, max_value=100, value=20, key="customer_page_size"
    )

    page = int(st.session_state.get("customer_page", 1))
    try:
        result = client.list_customers(
            q=q or None,
            customer_type=customer_type or None,
            status=status or None,
            page=page,
            page_size=int(page_size),
        )
    except CustomerAPIError as error:
        _show_error(error)
        return

    st.caption(f"{result['total']} customer(s) found")

    if not result["items"]:
        st.info("No customers match the current search.")
        return

    for item in result["items"]:
        with st.container(border=True):
            left, middle, right = st.columns([3, 2, 1])
            left.markdown(f"**{item['display_name']}**")
            left.caption(
                f"{item['customer_type'].title()} · {item['status'].title()} · v{item['version']}"
            )
            middle.write("Eligible" if item["eligible"] else "Not eligible")
            if right.button("Open", key=f"open_{item['id']}"):
                st.session_state["edit_customer_id"] = item["id"]
                st.session_state["customer_view"] = "edit"
                st.rerun()

    total_pages = max((result["total"] + result["page_size"] - 1) // result["page_size"], 1)
    previous, indicator, following = st.columns([1, 2, 1])
    if previous.button("Previous", disabled=page <= 1):
        st.session_state["customer_page"] = page - 1
        st.rerun()
    indicator.write(f"Page {page} of {total_pages}")
    if following.button("Next", disabled=page >= total_pages):
        st.session_state["customer_page"] = page + 1
        st.rerun()
