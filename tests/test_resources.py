"""Tests for VynFi resource modules."""

from __future__ import annotations

import httpx
import respx

from vynfi import VynFi

BASE = "https://api.vynfi.com"


@respx.mock
def test_generate_job() -> None:
    respx.post(f"{BASE}/v1/generate").mock(
        return_value=httpx.Response(
            202,
            json={
                "id": "job-123",
                "status": "queued",
                "credits_reserved": 500,
                "estimated_duration_seconds": 5,
            },
        )
    )
    client = VynFi(api_key="vf_test_abc")
    job = client.generate(tables=[{"name": "journal_entries", "rows": 500}])
    assert job.id == "job-123"
    assert job.status == "queued"
    assert job.credits_reserved == 500


@respx.mock
def test_list_jobs() -> None:
    respx.get(f"{BASE}/v1/jobs").mock(
        return_value=httpx.Response(
            200,
            json=[
                {"id": "j1", "status": "completed"},
                {"id": "j2", "status": "running"},
            ],
        )
    )
    client = VynFi(api_key="vf_test_abc")
    result = client.jobs.list()
    assert len(result.jobs) == 2
    assert result.jobs[0].id == "j1"


@respx.mock
def test_get_job() -> None:
    respx.get(f"{BASE}/v1/jobs/j1").mock(
        return_value=httpx.Response(200, json={"id": "j1", "status": "completed"})
    )
    client = VynFi(api_key="vf_test_abc")
    job = client.jobs.get("j1")
    assert job.status == "completed"


@respx.mock
def test_list_sectors() -> None:
    respx.get(f"{BASE}/v1/sectors").mock(
        return_value=httpx.Response(
            200,
            json=[
                {"slug": "retail", "name": "Retail", "table_count": 5},
                {"slug": "banking", "name": "Banking", "table_count": 8},
            ],
        )
    )
    client = VynFi(api_key="vf_test_abc")
    sectors = client.catalog.list_sectors()
    assert len(sectors) == 2
    assert sectors[0].slug == "retail"


@respx.mock
def test_get_sector() -> None:
    respx.get(f"{BASE}/v1/sectors/retail").mock(
        return_value=httpx.Response(
            200,
            json={
                "slug": "retail",
                "name": "Retail",
                "multiplier": 1.0,
                "tables": [
                    {"name": "journal_entries", "base_rate": 1.0, "columns": []},
                ],
            },
        )
    )
    client = VynFi(api_key="vf_test_abc")
    sector = client.catalog.get_sector("retail")
    assert sector.slug == "retail"
    assert len(sector.tables) == 1


@respx.mock
def test_usage_summary() -> None:
    respx.get(f"{BASE}/v1/usage/summary").mock(
        return_value=httpx.Response(
            200,
            json={"balance": 8500, "total_used": 1500, "burn_rate": 50.0, "period_days": 30},
        )
    )
    client = VynFi(api_key="vf_test_abc")
    usage = client.usage.summary()
    assert usage.balance == 8500
    assert usage.burn_rate == 50.0


@respx.mock
def test_create_api_key() -> None:
    respx.post(f"{BASE}/v1/api-keys").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": "key-1",
                "name": "CI key",
                "key": "vf_test_abc123def456",
                "prefix": "vf_test_abc",
            },
        )
    )
    client = VynFi(api_key="vf_test_abc")
    key = client.api_keys.create(name="CI key")
    assert key.key == "vf_test_abc123def456"


@respx.mock
def test_quality_scores() -> None:
    respx.get(f"{BASE}/v1/quality/scores").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": "qs1",
                    "job_id": "j1",
                    "overall_score": 0.92,
                    "benford_score": 0.95,
                    "correlation_score": 0.88,
                    "distribution_score": 0.91,
                },
            ],
        )
    )
    client = VynFi(api_key="vf_test_abc")
    scores = client.quality.scores()
    assert len(scores) == 1
    assert scores[0].overall_score == 0.92


@respx.mock
def test_create_webhook() -> None:
    respx.post(f"{BASE}/v1/webhooks").mock(
        return_value=httpx.Response(
            201,
            json={
                "id": "wh1",
                "url": "https://example.com/hook",
                "events": ["job.completed"],
                "secret": "whsec_abc123",
            },
        )
    )
    client = VynFi(api_key="vf_test_abc")
    hook = client.webhooks.create(url="https://example.com/hook", events=["job.completed"])
    assert hook.secret == "whsec_abc123"


@respx.mock
def test_billing_subscription() -> None:
    respx.get(f"{BASE}/v1/billing/subscription").mock(
        return_value=httpx.Response(
            200,
            json={"tier": "developer", "status": "active"},
        )
    )
    client = VynFi(api_key="vf_test_abc")
    sub = client.billing.subscription()
    assert sub.tier == "developer"
    assert sub.status == "active"
