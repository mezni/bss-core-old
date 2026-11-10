"""SQLAlchemy implementation of the order repository port."""

from __future__ import annotations

from sqlalchemy.orm import Session

from ..domain.entities import Order, OrderItem
from ..domain.exceptions import (
    OrderNotFound,
    StaleUpdate,
)
from ..domain.value_objects import OrderStatus
from ..infrastructure.orm import OrderItemORM, OrderORM


class SQLAlchemyOrderRepository:
    """Persist order aggregates in SQLAlchemy-backed tables."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, order: Order) -> Order:
        """Persist a new order aggregate."""
        orm = self._to_orm(order)
        self.session.add(orm)
        self._commit()
        self.session.refresh(orm)
        return self._to_domain(orm)

    def get(self, order_id: str) -> Order | None:
        """Return an order aggregate or None when it does not exist."""
        orm = self.session.get(OrderORM, order_id)
        if orm is None:
            return None
        return self._to_domain(orm)

    def update(self, order: Order, expected_version: int) -> Order:
        """Persist changes when expected_version matches the stored version."""
        orm = self.session.get(OrderORM, order.id)
        if orm is None:
            raise OrderNotFound(f"Order {order.id} was not found")
        if orm.version != expected_version:
            raise StaleUpdate(expected_version, orm.version)

        self._apply(orm, order)
        orm.version = expected_version + 1
        self._commit()
        self.session.refresh(orm)
        order.version = orm.version
        return self._to_domain(orm)

    def _apply(self, orm: OrderORM, order: Order) -> None:
        """Apply order changes to the ORM model."""
        orm.status = order.status.value
        orm.subtotal = order.subtotal
        orm.tax_amount = order.tax_amount
        orm.total = order.total
        orm.customer_id = order.customer_id
        orm.updated_at = order.updated_at

    def _to_orm(self, order: Order) -> OrderORM:
        """Convert a domain order to an ORM model."""
        items_orm: list[OrderItemORM] = []
        for item in order.items:
            items_orm.append(
                OrderItemORM(
                    id=item.id,
                    order_id=order.id,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.line_total,
                    created_at=item.created_at,
                )
            )

        return OrderORM(
            id=order.id,
            status=order.status.value,
            subtotal=order.subtotal,
            tax_amount=order.tax_amount,
            total=order.total,
            customer_id=order.customer_id,
            created_at=order.created_at,
            updated_at=order.updated_at,
            version=order.version,
            items=items_orm,
        )

    def _to_domain(self, orm: OrderORM) -> Order:
        """Convert an ORM model to a domain order."""
        items: list[OrderItem] = []
        for item in orm.items:
            items.append(
                OrderItem(
                    id=item.id,
                    description=item.description,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    line_total=item.line_total,
                    created_at=item.created_at,
                    order_id=orm.id,
                )
            )

        return Order(
            id=orm.id,
            status=OrderStatus(orm.status),  # Convert string to OrderStatus enum
            subtotal=float(orm.subtotal) if orm.subtotal else 0.0,
            tax_amount=float(orm.tax_amount) if orm.tax_amount else 0.0,
            total=float(orm.total) if orm.total else 0.0,
            customer_id=orm.customer_id,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
            version=orm.version,
            items=items,
        )