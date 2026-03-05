"""API key management resource."""

from __future__ import annotations

from typing import Any

from .._client import SyncClient
from .._types import ApiKey, ApiKeyCreated


class ApiKeys:
    """Manage API keys."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def create(
        self,
        *,
        name: str,
        scopes: list[str] | None = None,
        expires_in_days: int | None = None,
    ) -> ApiKeyCreated:
        """Create a new API key.

        The full key is only returned once in the response.
        """
        body: dict[str, Any] = {"name": name}
        if scopes is not None:
            body["scopes"] = scopes
        if expires_in_days is not None:
            body["expires_in_days"] = expires_in_days
        data = self._client.request("POST", "/v1/api-keys", json=body)
        return ApiKeyCreated.model_validate(data)

    def list(self) -> list[ApiKey]:
        """List all API keys (masked)."""
        data = self._client.request("GET", "/v1/api-keys")
        if isinstance(data, dict) and "keys" in data:
            data = data["keys"]
        return [ApiKey.model_validate(k) for k in data]

    def get(self, key_id: str) -> ApiKey:
        """Get API key details."""
        data = self._client.request("GET", f"/v1/api-keys/{key_id}")
        return ApiKey.model_validate(data)

    def update(
        self,
        key_id: str,
        *,
        name: str | None = None,
        scopes: list[str] | None = None,
    ) -> ApiKey:
        """Update an API key."""
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if scopes is not None:
            body["scopes"] = scopes
        data = self._client.request("PATCH", f"/v1/api-keys/{key_id}", json=body)
        return ApiKey.model_validate(data)

    def revoke(self, key_id: str) -> None:
        """Revoke (delete) an API key."""
        self._client.request("DELETE", f"/v1/api-keys/{key_id}")
