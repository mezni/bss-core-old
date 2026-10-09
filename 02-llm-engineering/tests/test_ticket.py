
import pytest


def test_ticket_contains_order_id():
    ticket = """
    My order #4821 has not arrived.
    It was supposed to arrive three days ago.
    Can you check the status?
    """

    assert "4821" in ticket


def test_ticket_is_not_empty():
    ticket = "My order #4821 has not arrived."

    assert ticket.strip() != ""


def test_ticket_contains_delivery_issue():
    ticket = "My order #4821 has not arrived."

    assert "not arrived" in ticket.lower()


@pytest.mark.parametrize(
    "ticket",
    [
        "My order #4821 has not arrived.",
        "I received the wrong item.",
        "I would like a refund for my purchase.",
    ],
)
def test_ticket_input_is_a_string(ticket):
    assert isinstance(ticket, str)
    assert ticket.strip()


def test_empty_ticket_is_detectable():
    ticket = "   "

    assert not ticket.strip()