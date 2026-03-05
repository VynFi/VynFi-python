"""Billing resource (read-only)."""

from __future__ import annotations

from .._client import SyncClient
from .._types import Invoice, PaymentMethod, Subscription


class Billing:
    """Read-only billing information."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def subscription(self) -> Subscription:
        """Get current subscription details."""
        data = self._client.request("GET", "/v1/billing/subscription")
        return Subscription.model_validate(data)

    def invoices(self) -> list[Invoice]:
        """Get invoice history."""
        data = self._client.request("GET", "/v1/billing/invoices")
        if isinstance(data, dict):
            data = data.get("invoices") or data.get("data") or []
        return [Invoice.model_validate(i) for i in data]

    def payment_method(self) -> PaymentMethod | None:
        """Get default payment method, if set."""
        data = self._client.request("GET", "/v1/billing/payment-method")
        if data is None:
            return None
        return PaymentMethod.model_validate(data)
