"""Usage analytics resource."""

from __future__ import annotations

from .._client import SyncClient
from .._types import DailyUsageResponse, UsageSummary


class Usage:
    """Credit usage analytics."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def summary(self, *, days: int = 30) -> UsageSummary:
        """Get usage summary for the given period.

        Args:
            days: Number of days to look back (1-365, default 30)
        """
        data = self._client.request("GET", "/v1/usage/summary", params={"days": days})
        return UsageSummary.model_validate(data)

    def daily(self, *, days: int = 30) -> DailyUsageResponse:
        """Get daily usage breakdown.

        Args:
            days: Number of days to look back (1-365, default 30)
        """
        data = self._client.request("GET", "/v1/usage/daily", params={"days": days})
        return DailyUsageResponse.model_validate(data)
