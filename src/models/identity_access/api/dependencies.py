"""Centralized authentication dependencies for the identity module.

Promotes the PyJWT permission-claim pattern (previously implemented per
module in the customer management API) into the identity module so every
workflow entry point shares one implementation (constitution Section 9,
research.md Decision 2).

- Bearer token, JWT HS256, signed with ``BSS_JWT_SECRET``
- ``permissions`` list claim carries role permissions
- Missing/invalid token -> 401 ``UNAUTHENTICATED``
- Valid token lacking the required permission -> 403 ``FORBIDDEN``
- ``user:admin`` grants every workflow (full access)
- Denials emit structured log events without token material (FR-005)
"""

from __future__ import annotations

import os
from typing import Callable

import jwt
from fastapi import Depends, Header, HTTPException, Request, status

from src.infrastructure.logging import log_authorization_denial

from .permissions import (
    USER_ADMIN,
    USER_BILLING,
    USER_VIEW,
    WORKFLOW_PERMISSIONS,
    WORKFLOW_CUSTOMER_TO_ORDER,
    WORKFLOW_INVOICE_TO_PAYMENT,
    WORKFLOW_ORDER_TO_INVOICE,
    WORKFLOW_ORDER_TO_SHIPMENT,
)

JWT_ALGORITHM = "HS256"
_DEV_SECRET = "bss-core-dev-secret"

# API path prefix -> workflow name, used to attribute 401 denials (raised
# before the route dependency knows the guarded workflow) to a workflow.
_WORKFLOW_PATHS: dict[str, str] = {
    "/api/v1/orders": WORKFLOW_CUSTOMER_TO_ORDER,
    "/api/v1/shipments": WORKFLOW_ORDER_TO_SHIPMENT,
    "/api/v1/invoices": WORKFLOW_ORDER_TO_INVOICE,
    "/api/v1/payments": WORKFLOW_INVOICE_TO_PAYMENT,
}


def _jwt_secret() -> str:
    return os.environ.get("BSS_JWT_SECRET", _DEV_SECRET)


def _workflow_for_request(request: Request) -> str | None:
    path = request.url.path.rstrip("/")
    for prefix, workflow in _WORKFLOW_PATHS.items():
        if path == prefix or path.startswith(prefix + "/"):
            return workflow
    return None


def get_permissions(
    request: Request,
    authorization: str | None = Header(default=None),
) -> set[str]:
    """Extract permissions from a signed bearer token."""
    workflow = _workflow_for_request(request)
    required = WORKFLOW_PERMISSIONS.get(workflow) if workflow else None
    if not authorization or not authorization.lower().startswith("bearer "):
        if required:
            log_authorization_denial(
                workflow=workflow, required_permission=required, result="unauthenticated"
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        if required:
            log_authorization_denial(
                workflow=workflow, required_permission=required, result="unauthenticated"
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    permissions = payload.get("permissions", [])
    if not isinstance(permissions, (list, tuple, set)):
        if required:
            log_authorization_denial(
                workflow=workflow, required_permission=required, result="unauthenticated"
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {str(permission) for permission in permissions}


def require_workflow_permission(workflow: str, permission: str) -> Callable[..., None]:
    """Build a dependency enforcing a workflow permission.

    ``user:admin`` satisfies every workflow; otherwise the exact dedicated
    permission is required. Denials are logged with the workflow name.
    """

    def _checker(permissions: set[str] = Depends(get_permissions)) -> None:
        if permission in permissions or USER_ADMIN in permissions:
            return
        log_authorization_denial(workflow=workflow, required_permission=permission)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Token lacks required permission '{permission}' for this workflow.",
        )

    return _checker


def require_user_view(permissions: set[str] = Depends(get_permissions)) -> None:
    """Require the ``user:view`` role permission (or ``user:admin``)."""
    if USER_VIEW not in permissions and USER_ADMIN not in permissions:
        log_authorization_denial(
            workflow=WORKFLOW_CUSTOMER_TO_ORDER, required_permission=USER_VIEW
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Token lacks required permission '{USER_VIEW}' for this workflow.",
        )


def require_user_billing(permissions: set[str] = Depends(get_permissions)) -> None:
    """Require the ``user:billing`` role permission (or ``user:admin``)."""
    if USER_BILLING not in permissions and USER_ADMIN not in permissions:
        log_authorization_denial(
            workflow=WORKFLOW_ORDER_TO_INVOICE, required_permission=USER_BILLING
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Token lacks required permission '{USER_BILLING}' for this workflow.",
        )


def require_user_admin(permissions: set[str] = Depends(get_permissions)) -> None:
    """Require the ``user:admin`` role permission."""
    if USER_ADMIN not in permissions:
        log_authorization_denial(
            workflow=WORKFLOW_ORDER_TO_SHIPMENT, required_permission=USER_ADMIN
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Token lacks required permission '{USER_ADMIN}' for this workflow.",
        )
