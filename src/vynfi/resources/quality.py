"""Quality scores resource."""

from __future__ import annotations

from .._client import SyncClient
from .._types import DailyQuality, QualityScore


class Quality:
    """Quality metrics for generated data."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def scores(self) -> list[QualityScore]:
        """List quality scores for all jobs."""
        data = self._client.request("GET", "/v1/quality/scores")
        if isinstance(data, dict) and "scores" in data:
            data = data["scores"]
        return [QualityScore.model_validate(s) for s in data]

    def timeline(self, *, days: int = 30) -> list[DailyQuality]:
        """Get daily quality averages.

        Args:
            days: Number of days to look back (default 30)
        """
        data = self._client.request("GET", "/v1/quality/timeline", params={"days": days})
        if isinstance(data, dict) and "timeline" in data:
            data = data["timeline"]
        return [DailyQuality.model_validate(d) for d in data]
