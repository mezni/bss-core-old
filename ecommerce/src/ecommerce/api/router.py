"""The reserved versioned route namespace.

The prefix is applied by the router itself, so any route added to it later inherits the
versioned path with no second registration step (FR-007). The router is mounted with no
routes: a description generated from an empty router is valid and truthfully reports that
there are no versioned endpoints yet, whereas a placeholder route would publish a
fictional endpoint (research.md D-07).
"""

from __future__ import annotations

from fastapi import APIRouter

from ecommerce.config import Settings


def build_versioned_router(settings: Settings) -> APIRouter:
    """Return the reserved router carrying the configured prefix and no routes."""
    return APIRouter(prefix=settings.api_v1_prefix)
