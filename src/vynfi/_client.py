"""Base HTTP client for VynFi API."""

from __future__ import annotations

import time
from typing import Any

import httpx

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

DEFAULT_BASE_URL = "https://api.vynfi.com"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 2
RETRY_STATUSES = {429, 500, 502, 503, 504}

_ERROR_MAP: dict[int, type[VynFiError]] = {
    401: AuthenticationError,
    402: InsufficientCreditsError,
    404: NotFoundError,
    409: ConflictError,
    422: ValidationError,
    429: RateLimitError,
}


class BaseClient:
    """Shared HTTP logic for sync and async clients."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        if not api_key:
            raise AuthenticationError("api_key is required")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "vynfi-python/0.1.0",
        }

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"


class SyncClient(BaseClient):
    """Synchronous HTTP client."""

    def __init__(self, api_key: str, **kwargs: Any) -> None:
        super().__init__(api_key, **kwargs)
        self._http = httpx.Client(
            headers=self._headers(),
            timeout=self.timeout,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> SyncClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        params: dict[str, Any] | None = None,
    ) -> Any:
        url = self._url(path)
        last_exc: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                resp = self._http.request(method, url, json=json, params=params)
            except httpx.HTTPError as e:
                last_exc = e
                if attempt < self.max_retries:
                    time.sleep(2**attempt * 0.5)
                    continue
                raise VynFiError(f"HTTP request failed: {e}") from e

            if resp.status_code in RETRY_STATUSES and attempt < self.max_retries:
                time.sleep(2**attempt * 0.5)
                continue

            if resp.status_code >= 400:
                _raise_for_status(resp)

            if resp.status_code == 204:
                return None

            return resp.json()

        raise VynFiError("Max retries exceeded") from last_exc

    def request_raw(self, method: str, path: str) -> httpx.Response:
        """Return the raw httpx.Response (for streaming/download)."""
        url = self._url(path)
        resp = self._http.request(method, url)
        if resp.status_code >= 400:
            _raise_for_status(resp)
        return resp

    def stream_sse(self, path: str) -> Any:
        """Yield SSE events from a streaming endpoint."""
        url = self._url(path)
        with self._http.stream("GET", url) as resp:
            if resp.status_code >= 400:
                resp.read()
                _raise_for_status(resp)
            event_type = ""
            data_lines: list[str] = []
            for line in resp.iter_lines():
                if line.startswith("event: "):
                    event_type = line[7:]
                elif line.startswith("data: "):
                    data_lines.append(line[6:])
                elif line == "" and data_lines:
                    import json

                    data_str = "\n".join(data_lines)
                    try:
                        data = json.loads(data_str)
                    except (ValueError, TypeError):
                        data = data_str
                    yield {"event": event_type, "data": data}
                    event_type = ""
                    data_lines = []


def _raise_for_status(resp: httpx.Response) -> None:
    """Raise the appropriate VynFiError subclass."""
    try:
        body = resp.json()
    except Exception:
        body = {"detail": resp.text}

    message = body.get("detail", body.get("message", f"HTTP {resp.status_code}"))
    if isinstance(message, str):
        pass
    else:
        message = str(message)

    exc_class = _ERROR_MAP.get(resp.status_code)
    if exc_class is None:
        exc_class = ServerError if resp.status_code >= 500 else VynFiError

    raise exc_class(message, status_code=resp.status_code, body=body)
