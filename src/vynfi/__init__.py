"""VynFi Python SDK — synthetic financial data generation."""

from __future__ import annotations

from typing import Any

from ._client import SyncClient
from ._exceptions import (
    AuthenticationError,
    ConflictError,
    InsufficientCreditsError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
    VynFiError,
)
from ._types import (
    ApiKey,
    ApiKeyCreated,
    CatalogItem,
    DailyQuality,
    DailyUsage,
    Fingerprint,
    Invoice,
    Job,
    JobList,
    PaymentMethod,
    QualityScore,
    Sector,
    SectorSummary,
    SubmitJobResponse,
    Subscription,
    UsageSummary,
    Webhook,
    WebhookCreated,
)
from .resources.api_keys import ApiKeys
from .resources.billing import Billing
from .resources.catalog import Catalog
from .resources.jobs import Jobs
from .resources.quality import Quality
from .resources.usage import Usage
from .resources.webhooks import Webhooks

__version__ = "0.1.0"
__all__ = [
    "VynFi",
    "VynFiError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    "Job",
    "JobList",
    "SubmitJobResponse",
    "Sector",
    "SectorSummary",
    "CatalogItem",
    "Fingerprint",
    "UsageSummary",
    "DailyUsage",
    "ApiKey",
    "ApiKeyCreated",
    "QualityScore",
    "DailyQuality",
    "Webhook",
    "WebhookCreated",
    "Subscription",
    "Invoice",
    "PaymentMethod",
]


class VynFi:
    """VynFi API client.

    Usage::

        from vynfi import VynFi

        client = VynFi(api_key="vf_live_...")

        # Generate data
        job = client.jobs.generate(
            tables=[{"name": "journal_entries", "rows": 5000}],
            format="json",
        )

        # Check usage
        usage = client.usage.summary()
        print(f"Balance: {usage.balance} credits")

        # Browse catalog
        sectors = client.catalog.list_sectors()
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.vynfi.com",
        timeout: float = 30.0,
        max_retries: int = 2,
    ) -> None:
        self._client = SyncClient(
            api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )
        self.jobs = Jobs(self._client)
        self.catalog = Catalog(self._client)
        self.usage = Usage(self._client)
        self.api_keys = ApiKeys(self._client)
        self.quality = Quality(self._client)
        self.webhooks = Webhooks(self._client)
        self.billing = Billing(self._client)

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> VynFi:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ── Convenience shortcuts ──

    def generate(self, **kwargs: Any) -> SubmitJobResponse:
        """Shortcut for client.jobs.generate(...)."""
        return self.jobs.generate(**kwargs)

    def generate_quick(self, **kwargs: Any) -> Job:
        """Shortcut for client.jobs.generate_quick(...)."""
        return self.jobs.generate_quick(**kwargs)
