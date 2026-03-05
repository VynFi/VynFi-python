# VynFi Python SDK Design

> **Status:** Approved
> **Date:** 2026-03-05

## Goal

Python client library for the VynFi API, published to PyPI as `vynfi`.

## Decisions

- **HTTP client:** httpx (sync + async)
- **Models:** pydantic v2 for typed responses
- **Auth:** API key only (vf_live_/vf_test_ prefix)
- **Pattern:** Resource namespaces (client.jobs.list())
- **Python:** 3.9+
- **License:** Apache 2.0

## Phase 1 Scope

Generate, Jobs, Catalog/Sectors, Usage, API Keys, Quality, Webhooks, Billing (read-only).

Excluded: Portal auth, teams, marketplace, fingerprints, settings/notifications.

## Package Structure

```
vynfi/
  __init__.py          # VynFi class, exports
  _client.py           # Base HTTP client
  _exceptions.py       # Error hierarchy
  _types.py            # Pydantic response models
  resources/
    jobs.py            # Jobs + Generate
    catalog.py         # Sectors + Catalog
    usage.py           # Usage analytics
    api_keys.py        # Key management
    quality.py         # Quality scores
    webhooks.py        # Webhook CRUD
    billing.py         # Billing read-only
```

## Error Mapping

| HTTP Status | Exception |
|-------------|-----------|
| 401 | AuthenticationError |
| 402 | InsufficientCreditsError |
| 404 | NotFoundError |
| 422 | ValidationError |
| 429 | RateLimitError |
| 5xx | ServerError |
