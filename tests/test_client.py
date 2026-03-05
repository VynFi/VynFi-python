"""Tests for the VynFi base client."""

from __future__ import annotations

import httpx
import pytest
import respx

from vynfi import AuthenticationError, NotFoundError, RateLimitError, ServerError, VynFi

BASE = "https://api.vynfi.com"


def test_requires_api_key() -> None:
    with pytest.raises(AuthenticationError):
        VynFi(api_key="")


@respx.mock
def test_authentication_header() -> None:
    route = respx.get(f"{BASE}/v1/usage/summary").mock(
        return_value=httpx.Response(200, json={"balance": 1000})
    )
    client = VynFi(api_key="vf_test_abc123")
    client.usage.summary()
    assert route.called
    assert route.calls[0].request.headers["authorization"] == "Bearer vf_test_abc123"


@respx.mock
def test_404_raises_not_found() -> None:
    respx.get(f"{BASE}/v1/jobs/nonexistent").mock(
        return_value=httpx.Response(404, json={"detail": "Job not found"})
    )
    client = VynFi(api_key="vf_test_abc")
    with pytest.raises(NotFoundError, match="Job not found"):
        client.jobs.get("nonexistent")


@respx.mock
def test_429_raises_rate_limit() -> None:
    respx.get(f"{BASE}/v1/jobs").mock(
        return_value=httpx.Response(429, json={"detail": "Too many requests"})
    )
    client = VynFi(api_key="vf_test_abc", max_retries=0)
    with pytest.raises(RateLimitError):
        client.jobs.list()


@respx.mock
def test_500_raises_server_error() -> None:
    respx.get(f"{BASE}/v1/jobs").mock(
        return_value=httpx.Response(500, json={"detail": "Internal error"})
    )
    client = VynFi(api_key="vf_test_abc", max_retries=0)
    with pytest.raises(ServerError):
        client.jobs.list()


@respx.mock
def test_retry_on_429() -> None:
    route = respx.get(f"{BASE}/v1/usage/summary").mock(
        side_effect=[
            httpx.Response(429, json={"detail": "rate limited"}),
            httpx.Response(200, json={"balance": 500}),
        ]
    )
    client = VynFi(api_key="vf_test_abc", max_retries=1)
    result = client.usage.summary()
    assert result.balance == 500
    assert route.call_count == 2
