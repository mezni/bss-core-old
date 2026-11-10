"""Order aggregate and child entities."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from .exceptions import InvalidOrder, OrderItemError
from .value_objects import OrderStatus


def utcnow() -> datetime:
    """Return the current timezone-aware UTC timestamp."""
    return datetime.now(UTC)


def normalize_datetime(value: datetime) -> datetime:
    """Attach UTC to naive datetimes returned by SQLite."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


@dataclass
class OrderItem:
    """An item within an order."""

    id: str
    description: str
    quantity: float
    unit_price: float
    line_total: float
    created_at: datetime
    order_id: str | None = None

    def __post_init__(self) -> None:
        self.description = self.description.strip()
        if not self.description:
            raise OrderItemError("Item description is required")
        if self.quantity <= 0:
            raise OrderItemError("Quantity must be greater than zero")
        if self.unit_price < 0:
            raise OrderItemError("Unit price must be non-negative")
        self.created_at = normalize_datetime(self.created_at)


@dataclass
class Order:
    """Aggregate root for order management."""

    id: str
    status: OrderStatus
    subtotal: float
    tax_amount: float
    total: float
    customer_id: str
    created_at: datetime
    updated_at: datetime
    version: int
    items: list[OrderItem] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.created_at = normalize_datetime(self.created_at)
        self.updated_at = normalize_datetime(self.updated_at)
        self.validate()

    @classmethod
    def create(
        cls,
        customer_id: str,
        items: list[dict[str, Any]] | None = None,
        order_id: str | None = None,
    ) -> Order:
        """Create a new order in draft status requiring at least one order item."""
        now = utcnow()
        order_id = order_id or str(uuid4())
        items = items or []
        if len(items) == 0:
            raise InvalidOrder("At least one order item is required to create an order")

        order_items: list[OrderItem] = []
        subtotal = 0.0
        for item_data in items:
            description = item_data.get("description", "").strip()
            quantity = float(item_data.get("quantity", 1))
            unit_price = float(item_data.get("unit_price", 0))

            if not description:
                raise OrderItemError("Item description is required")
            if quantity <= 0:
                raise OrderItemError("Quantity must be greater than zero")
            if unit_price < 0:
                raise OrderItemError("Unit price must be non-negative")

            line_total = round(quantity * unit_price, 2)
            item = OrderItem(
                id=str(uuid4()),
                description=description,
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total,
                created_at=now,
                order_id=order_id,
            )
            order_items.append(item)
            subtotal += line_total

        tax_rate = 0.10  # S03 MVP fixed tax rate
        tax_amount = round(subtotal * tax_rate, 2)
        total = round(subtotal + tax_amount, 2)

        return cls(
            id=order_id,
            status=OrderStatus.DRAFT,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total=total,
            customer_id=customer_id,
            created_at=now,
            updated_at=now,
            version=1,
            items=order_items,
        )

    def validate(self) -> None:
        """Validate order invariants."""
        if self.status == OrderStatus.CANCELLED and self.version > 1:
            raise InvalidOrder("Cancelled orders cannot be modified")
        if not self.items and self.status != OrderStatus.CANCELLED:
            raise InvalidOrder("Order must have at least one item")

    def can_be_confirmed(self) -> bool:
        """Check if order can be confirmed (must have at least one item)."""
        return len(self.items) >= 1 and self.status == OrderStatus.DRAFT

    def can_be_cancelled(self) -> bool:
        """Check if order can be cancelled (only in draft state)."""
        return self.status == OrderStatus.DRAFT

    def confirm(self) -> Order:
        """Confirm the order (draft → confirmed)."""
        if not self.can_be_confirmed():
            raise InvalidOrder(
                "Order can only be confirmed if it has at least one item and is in draft status"
            )
        self.status = OrderStatus.CONFIRMED
        self.updated_at = utcnow()
        self.version += 1
        return self

    def ship(self) -> Order:
        """Ship the order (confirmed → shipped)."""
        if self.status != OrderStatus.CONFIRMED:
            raise InvalidOrder("Order can only be shipped if it is in confirmed status")
        self.status = OrderStatus.SHIPPED
        self.updated_at = utcnow()
        self.version += 1
        return self

    def deliver(self) -> Order:
        """Deliver the order (shipped → delivered)."""
        if self.status != OrderStatus.SHIPPED:
            raise InvalidOrder("Order can only be delivered if it is in shipped status")
        self.status = OrderStatus.DELIVERED
        self.updated_at = utcnow()
        self.version += 1
        return self

    def cancel(self) -> Order:
        """Cancel the order (draft → cancelled, terminal)."""
        if not self.can_be_cancelled():
            raise InvalidOrder("Order can only be cancelled if it is in draft status")
        self.status = OrderStatus.CANCELLED
        self.updated_at = utcnow()
        self.version += 1
        return self

    def revert(self) -> Order:
        """Revert a cancelled order (not allowed - terminal state)."""
        raise InvalidOrder("Cancelled orders are terminal and cannot be restored")
        # Note: In a real system, this would be a no-op or raise an error
        # Per constitution: "Cancellation is terminal; orders in cancelled state cannot be restored"

    def add_item(self, item: OrderItem) -> Order:
        """Add an item to the order."""
        self.items.append(item)
        self.updated_at = utcnow()
        self.version += 1
        return self

    def remove_item(self, item_id: str) -> Order:
        """Remove an item from the order by ID."""
        self.items = [item for item in self.items if item.id != item_id]
        self.updated_at = utcnow()
        self.version += 1
        return self

    def update_item_quantity(self, item_id: str, quantity: float) -> Order:
        """Update the quantity of an existing item."""
        for item in self.items:
            if item.id == item_id:
                if quantity <= 0:
                    raise OrderItemError("Quantity must be greater than zero")
                item.quantity = quantity
                item.line_total = round(quantity * item.unit_price, 2)
                self.updated_at = utcnow()
                self.version += 1
                return self
        raise InvalidOrder(f"Item {item_id} not found in order")

    def calculate_totals(self) -> Order:
        """Recalculate order totals from items."""
        subtotal = sum(item.line_total for item in self.items)
        tax_rate = 0.10  # S03 MVP fixed tax rate
        tax_amount = round(subtotal * tax_rate, 2)
        total = round(subtotal + tax_amount, 2)
        self.subtotal = subtotal
        self.tax_amount = tax_amount
        self.total = total
        self.updated_at = utcnow()
        self.version += 1
        return self
