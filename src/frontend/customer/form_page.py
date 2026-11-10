"""Customer create/edit forms with contact and address management."""

from __future__ import annotations

from typing import Any

import streamlit as st

from .api_client import CustomerAPIClient, CustomerAPIError

CONTACT_TYPES = ["EMAIL", "PHONE"]


def _show_error(error: CustomerAPIError) -> None:
    st.error(f"{error.code}: {error.message}")


def _identity_fields(customer_type: str, customer: dict[str, Any] | None = None):
    customer = customer or {}
    if customer_type == "INDIVIDUAL":
        first_name = st.text_input("First name", value=customer.get("first_name") or "")
        last_name = st.text_input("Last name", value=customer.get("last_name") or "")
        email = st.text_input("Email", value=customer.get("email") or "")
        return {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        }
    legal_name = st.text_input("Legal name", value=customer.get("legal_name") or "")
    registration_number = st.text_input(
        "Registration / tax ID", value=customer.get("registration_number") or ""
    )
    email = st.text_input("General email (optional)", value=customer.get("email") or "")
    return {
        "legal_name": legal_name,
        "registration_number": registration_number,
        "email": email or None,
    }


def render_create_page(client: CustomerAPIClient) -> None:
    """Render the customer registration form."""
    st.header("New customer")
    customer_type = st.selectbox(
        "Customer type", ["INDIVIDUAL", "BUSINESS"], key="new_customer_type"
    )

    with st.form("create_customer"):
        display_name = st.text_input("Display name")
        fields = _identity_fields(customer_type)
        submitted = st.form_submit_button("Create customer")

    if not submitted:
        return

    payload: dict[str, Any] = {
        "customer_type": customer_type,
        "display_name": display_name,
        **fields,
    }
    if payload.get("email") is None:
        payload.pop("email", None)

    try:
        created = client.create_customer(payload)
    except CustomerAPIError as error:
        _show_error(error)
        return

    st.success(f"Created {created['display_name']}")
    st.session_state["edit_customer_id"] = created["id"]
    st.session_state["customer_view"] = "edit"
    st.rerun()


def render_edit_page(client: CustomerAPIClient, customer_id: str) -> None:
    """Render the edit form plus contact/address management."""
    try:
        customer = client.get_customer(customer_id)
    except CustomerAPIError as error:
        _show_error(error)
        return

    st.header(customer["display_name"])
    st.caption(
        f"{customer['customer_type'].title()} · {customer['status'].title()} · "
        f"v{customer['version']} · "
        + ("eligible" if customer["eligible"] else "not eligible")
    )

    if customer["status"] == "ACTIVE":
        if st.button("Deactivate customer"):
            try:
                client.deactivate_customer(customer_id)
                st.rerun()
            except CustomerAPIError as error:
                _show_error(error)
    else:
        if st.button("Reactivate customer"):
            try:
                client.reactivate_customer(customer_id)
                st.rerun()
            except CustomerAPIError as error:
                _show_error(error)

    customer_type = st.selectbox(
        "Customer type",
        ["INDIVIDUAL", "BUSINESS"],
        index=0 if customer["customer_type"] == "INDIVIDUAL" else 1,
        key=f"edit_type_{customer_id}",
    )

    with st.form(f"edit_customer_{customer_id}"):
        display_name = st.text_input("Display name", value=customer["display_name"])
        fields = _identity_fields(customer_type, customer)
        submitted = st.form_submit_button("Save changes")

    if submitted:
        payload: dict[str, Any] = {
            "version": customer["version"],
            "display_name": display_name,
            **fields,
        }
        if customer_type != customer["customer_type"]:
            payload["customer_type"] = customer_type
        if payload.get("email") is None:
            payload.pop("email", None)
        try:
            client.update_customer(customer_id, payload)
        except CustomerAPIError as error:
            _show_error(error)
        else:
            st.rerun()

    _render_contacts(client, customer)
    _render_addresses(client, customer)


def _render_contacts(client: CustomerAPIClient, customer: dict[str, Any]) -> None:
    st.subheader("Contacts")
    if not customer["contacts"]:
        st.caption("No contacts yet. At least one contact is required for eligibility.")

    for contact in customer["contacts"]:
        with st.expander(
            f"{contact['name']} · {contact['contact_type']} · {contact['value']}"
        ):
            with st.form(f"edit_contact_{contact['id']}"):
                name = st.text_input("Name", value=contact["name"])
                contact_type = st.selectbox(
                    "Type",
                    CONTACT_TYPES,
                    index=CONTACT_TYPES.index(contact["contact_type"]),
                )
                value = st.text_input("Value", value=contact["value"])
                is_primary = st.checkbox("Primary", value=contact["is_primary"])
                if st.form_submit_button("Save contact"):
                    try:
                        client.update_contact(
                            customer["id"],
                            contact["id"],
                            {
                                "version": customer["version"],
                                "name": name,
                                "contact_type": contact_type,
                                "value": value,
                                "is_primary": is_primary,
                            },
                        )
                    except CustomerAPIError as error:
                        _show_error(error)
                    else:
                        st.rerun()
            if st.button("Delete contact", key=f"delete_contact_{contact['id']}"):
                try:
                    client.remove_contact(
                        customer["id"], contact["id"], customer["version"]
                    )
                except CustomerAPIError as error:
                    _show_error(error)
                else:
                    st.rerun()

    with st.form(f"add_contact_{customer['id']}"):
        name = st.text_input("Name", key=f"new_contact_name_{customer['id']}")
        contact_type = st.selectbox(
            "Type", CONTACT_TYPES, key=f"new_contact_type_{customer['id']}"
        )
        value = st.text_input("Value", key=f"new_contact_value_{customer['id']}")
        is_primary = st.checkbox(
            "Primary", key=f"new_contact_primary_{customer['id']}"
        )
        if st.form_submit_button("Add contact"):
            try:
                client.add_contact(
                    customer["id"],
                    {
                        "name": name,
                        "contact_type": contact_type,
                        "value": value,
                        "is_primary": is_primary,
                    },
                )
            except CustomerAPIError as error:
                _show_error(error)
            else:
                st.rerun()


def _render_addresses(client: CustomerAPIClient, customer: dict[str, Any]) -> None:
    st.subheader("Addresses")
    if not customer["addresses"]:
        st.caption("No addresses yet. At least one address is required for eligibility.")

    for address in customer["addresses"]:
        with st.expander(
            f"{address['label'] or 'Address'} · {address['line1']}, {address['city']}"
        ):
            with st.form(f"edit_address_{address['id']}"):
                label = st.text_input("Label", value=address["label"] or "")
                line1 = st.text_input("Line 1", value=address["line1"])
                line2 = st.text_input("Line 2", value=address["line2"] or "")
                city = st.text_input("City", value=address["city"])
                region = st.text_input("Region", value=address["region"] or "")
                postal_code = st.text_input("Postal code", value=address["postal_code"])
                country = st.text_input("Country (ISO-2)", value=address["country"])
                is_primary = st.checkbox("Primary", value=address["is_primary"])
                if st.form_submit_button("Save address"):
                    try:
                        client.update_address(
                            customer["id"],
                            address["id"],
                            {
                                "version": customer["version"],
                                "label": label or None,
                                "line1": line1,
                                "line2": line2 or None,
                                "city": city,
                                "region": region or None,
                                "postal_code": postal_code,
                                "country": country,
                                "is_primary": is_primary,
                            },
                        )
                    except CustomerAPIError as error:
                        _show_error(error)
                    else:
                        st.rerun()
            if st.button("Delete address", key=f"delete_address_{address['id']}"):
                try:
                    client.remove_address(
                        customer["id"], address["id"], customer["version"]
                    )
                except CustomerAPIError as error:
                    _show_error(error)
                else:
                    st.rerun()

    with st.form(f"add_address_{customer['id']}"):
        label = st.text_input("Label", key=f"new_address_label_{customer['id']}")
        line1 = st.text_input("Line 1", key=f"new_address_line1_{customer['id']}")
        line2 = st.text_input("Line 2", key=f"new_address_line2_{customer['id']}")
        city = st.text_input("City", key=f"new_address_city_{customer['id']}")
        region = st.text_input("Region", key=f"new_address_region_{customer['id']}")
        postal_code = st.text_input(
            "Postal code", key=f"new_address_postal_{customer['id']}"
        )
        country = st.text_input(
            "Country (ISO-2)", value="US", key=f"new_address_country_{customer['id']}"
        )
        is_primary = st.checkbox(
            "Primary", key=f"new_address_primary_{customer['id']}"
        )
        if st.form_submit_button("Add address"):
            try:
                client.add_address(
                    customer["id"],
                    {
                        "label": label or None,
                        "line1": line1,
                        "line2": line2 or None,
                        "city": city,
                        "region": region or None,
                        "postal_code": postal_code,
                        "country": country,
                        "is_primary": is_primary,
                    },
                )
            except CustomerAPIError as error:
                _show_error(error)
            else:
                st.rerun()
