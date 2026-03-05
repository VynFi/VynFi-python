"""Jobs and data generation resource."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

from .._client import SyncClient
from .._types import Job, JobList, SubmitJobResponse


class Jobs:
    """Manage generation jobs."""

    def __init__(self, client: SyncClient) -> None:
        self._client = client

    def generate(
        self,
        *,
        tables: list[dict[str, Any]],
        format: str = "json",
        sector_slug: str = "retail",
    ) -> SubmitJobResponse:
        """Submit an async generation job.

        Args:
            tables: List of table specs, e.g. [{"name": "journal_entries", "rows": 5000}]
            format: Output format — "json", "csv", or "parquet"
            sector_slug: Sector to generate from
        """
        body: dict[str, Any] = {
            "tables": tables,
            "format": format,
            "sector_slug": sector_slug,
        }
        data = self._client.request("POST", "/v1/generate", json=body)
        return SubmitJobResponse.model_validate(data)

    def generate_quick(
        self,
        *,
        tables: list[dict[str, Any]],
        format: str = "json",
        sector_slug: str = "retail",
    ) -> Job:
        """Submit a synchronous (quick) generation job.

        Returns the completed job directly. Best for small datasets.
        """
        body: dict[str, Any] = {
            "tables": tables,
            "format": format,
            "sector_slug": sector_slug,
        }
        data = self._client.request("POST", "/v1/generate/quick", json=body)
        return Job.model_validate(data)

    def list(
        self,
        *,
        limit: int = 20,
        status: str | None = None,
        after: str | None = None,
        before: str | None = None,
    ) -> JobList:
        """List jobs with optional filtering."""
        params: dict[str, Any] = {"limit": limit}
        if status:
            params["status"] = status
        if after:
            params["after"] = after
        if before:
            params["before"] = before
        data = self._client.request("GET", "/v1/jobs", params=params)
        if isinstance(data, list):
            return JobList(jobs=[Job.model_validate(j) for j in data])
        return JobList.model_validate(data)

    def get(self, job_id: str) -> Job:
        """Get a single job by ID."""
        data = self._client.request("GET", f"/v1/jobs/{job_id}")
        return Job.model_validate(data)

    def cancel(self, job_id: str) -> Job:
        """Cancel a queued or running job."""
        data = self._client.request("DELETE", f"/v1/jobs/{job_id}")
        return Job.model_validate(data)

    def stream(self, job_id: str) -> Iterator[dict[str, Any]]:
        """Stream SSE progress events for a job.

        Yields dicts with 'event' and 'data' keys.
        Events: progress, complete, error.
        """
        yield from self._client.stream_sse(f"/v1/jobs/{job_id}/stream")

    def download(self, job_id: str, path: str | Path) -> Path:
        """Download job output to a local file.

        Args:
            job_id: The job ID
            path: Local file path to write to

        Returns:
            The Path where the file was saved
        """
        resp = self._client.request_raw("GET", f"/v1/jobs/{job_id}/download")
        out = Path(path)
        out.write_bytes(resp.content)
        return out
