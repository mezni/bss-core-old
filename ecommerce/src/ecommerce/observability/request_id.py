"""Request identifier resolution.

The error envelope mandates a ``request_id`` on every failure, so something must produce
it. This module owns exactly that one responsibility. It deliberately does not log, does
not emit metrics, and registers no tracing: structured logging and metrics belong to the
observability feature, and inventing a log format here would be churn when that feature
decides one (see research.md D-06).

A client-supplied ``X-Request-ID`` is honoured so a caller can correlate its own logs with
the server's, but it is truncated and character-screened first. An unbounded
client-controlled value reflected into every error response is a log- and
header-injection surface.
"""

from __future__ import annotations

import re
import uuid

#: Request state key under which the resolved identifier is stored.
REQUEST_ID_KEY = "request_id"

#: Header a caller may set to supply its own correlation identifier.
REQUEST_ID_HEADER = "X-Request-ID"

#: Upper bound on an accepted inbound identifier.
MAX_INBOUND_LENGTH = 64

#: Identifiers are restricted to characters that are safe to echo into a response and to
#: write into a log line: no whitespace, no quotes, no angle brackets, no separators.
_ALLOWED = re.compile(r"\A[A-Za-z0-9._:@\-]+\Z")


def sanitize_inbound(value: str | None) -> str | None:
    """Return a safe identifier from a client-supplied value, or ``None``.

    ``None`` means the caller should generate a fresh identifier. Rejection is
    deliberately silent to the client: the server substitutes its own value rather than
    returning an error, because a malformed correlation header must not fail a request.
    """
    if value is None:
        return None
    candidate = value.strip()
    if not candidate or len(candidate) > MAX_INBOUND_LENGTH:
        return None
    if not _ALLOWED.fullmatch(candidate):
        return None
    return candidate


def resolve_request_id(inbound: str | None = None) -> str:
    """Resolve the identifier for a request: the inbound value if acceptable, else a UUID4."""
    return sanitize_inbound(inbound) or str(uuid.uuid4())
