"""Catalog and sectors resource."""

from __future__ import annotations

from typing import Any

from .._client import SyncClient
from .._types import CatalogItem, Fingerprint, Sector, SectorSummary


class Catalog:
    """Browse sector catalog and fingerprints."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def list_sectors(self) -> list[SectorSummary]:
        """List all available sectors."""
        data = self._client.request("GET", "/v1/sectors")
        if isinstance(data, dict) and "sectors" in data:
            data = data["sectors"]
        return [SectorSummary.model_validate(s) for s in data]

    def get_sector(self, slug: str) -> Sector:
        """Get sector detail with table definitions."""
        data = self._client.request("GET", f"/v1/sectors/{slug}")
        return Sector.model_validate(data)

    def list(
        self,
        *,
        sector: str | None = None,
        search: str | None = None,
        source: str | None = None,
    ) -> list[CatalogItem]:
        """Browse the fingerprint catalog."""
        params: dict[str, Any] = {}
        if sector:
            params["sector"] = sector
        if search:
            params["search"] = search
        if source:
            params["source"] = source
        data = self._client.request("GET", "/v1/catalog", params=params)
        if isinstance(data, dict) and "items" in data:
            data = data["items"]
        return [CatalogItem.model_validate(item) for item in data]

    def get_fingerprint(self, sector: str, profile: str) -> Fingerprint:
        """Get a fingerprint's detail including column definitions."""
        data = self._client.request("GET", f"/v1/catalog/{sector}/{profile}")
        return Fingerprint.model_validate(data)
