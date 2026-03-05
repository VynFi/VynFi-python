"""Webhook management resource."""

from __future__ import annotations

from typing import Any

from .._client import SyncClient
from .._types import Webhook, WebhookCreated


class Webhooks:
    """Manage webhooks."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def create(self, *, url: str, events: list[str]) -> WebhookCreated:
        """Create a new webhook.

        Args:
            url: HTTPS endpoint URL
            events: Event types to subscribe to
                    (job.completed, job.failed, usage.threshold, key.expiring)
        """
        data = self._client.request("POST", "/v1/webhooks", json={"url": url, "events": events})
        return WebhookCreated.model_validate(data)

    def list(self) -> list[Webhook]:
        """List all webhooks."""
        data = self._client.request("GET", "/v1/webhooks")
        if isinstance(data, dict):
            data = data.get("webhooks") or data.get("data") or []
        return [Webhook.model_validate(w) for w in data]

    def get(self, webhook_id: str) -> Webhook:
        """Get webhook details."""
        data = self._client.request("GET", f"/v1/webhooks/{webhook_id}")
        return Webhook.model_validate(data)

    def update(
        self,
        webhook_id: str,
        *,
        url: str | None = None,
        events: list[str] | None = None,
        status: str | None = None,
    ) -> Webhook:
        """Update a webhook."""
        body: dict[str, Any] = {}
        if url is not None:
            body["url"] = url
        if events is not None:
            body["events"] = events
        if status is not None:
            body["status"] = status
        data = self._client.request("PATCH", f"/v1/webhooks/{webhook_id}", json=body)
        return Webhook.model_validate(data)

    def delete(self, webhook_id: str) -> None:
        """Delete a webhook."""
        self._client.request("DELETE", f"/v1/webhooks/{webhook_id}")

    def test(self, webhook_id: str) -> dict[str, Any]:
        """Send a test event to a webhook."""
        data = self._client.request("POST", f"/v1/webhooks/{webhook_id}/test")
        return data  # type: ignore[return-value]
