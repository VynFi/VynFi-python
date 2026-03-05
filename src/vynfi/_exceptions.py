"""VynFi API error hierarchy."""

from __future__ import annotations

from typing import Any


class VynFiError(Exception):
    """Base exception for all VynFi API errors."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        body: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class AuthenticationError(VynFiError):
    """401 — invalid or missing API key."""


class InsufficientCreditsError(VynFiError):
    """402 — not enough credits for the requested operation."""


class NotFoundError(VynFiError):
    """404 — requested resource does not exist."""


class ConflictError(VynFiError):
    """409 — resource already exists or state conflict."""


class ValidationError(VynFiError):
    """422 — request body failed validation."""


class RateLimitError(VynFiError):
    """429 — too many requests."""


class ServerError(VynFiError):
    """5xx — server-side error."""
