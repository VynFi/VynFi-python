# VynFi Python SDK

The official Python client for the [VynFi](https://vynfi.com) synthetic financial data API.

## Installation

```bash
pip install vynfi
```

## Quick Start

```python
from vynfi import VynFi

client = VynFi(api_key="vf_live_...")

# Generate synthetic financial data
job = client.generate(
    tables=[{"name": "journal_entries", "rows": 5000}],
    format="json",
    sector_slug="retail",
)
print(f"Job {job.id} submitted ({job.credits_reserved} credits)")

# Poll until complete
import time
while True:
    status = client.jobs.get(job.id)
    if status.status in ("completed", "failed"):
        break
    time.sleep(2)

# Download the result
if status.status == "completed":
    client.jobs.download(job.id, "output.json")
```

## Usage

### Browse the catalog

```python
sectors = client.catalog.list_sectors()
for s in sectors:
    print(f"{s.name} ({s.slug})")

sector = client.catalog.get_sector("retail")
for table in sector.tables:
    print(f"  {table.name}: {len(table.columns)} columns")
```

### Check credit usage

```python
usage = client.usage.summary(days=30)
print(f"Balance: {usage.balance} credits")
print(f"Burn rate: {usage.burn_rate}/day")
```

### Manage API keys

```python
keys = client.api_keys.list()
new_key = client.api_keys.create(name="CI pipeline")
print(f"Key: {new_key.key}")  # Only shown once!
```

### Quality scores

```python
scores = client.quality.scores()
for s in scores:
    print(f"Job {s.job_id}: {s.overall_score:.2f}")
```

### Webhooks

```python
hook = client.webhooks.create(
    url="https://example.com/webhook",
    events=["job.completed", "job.failed"],
)
print(f"Webhook secret: {hook.secret}")
```

### Stream job progress (SSE)

```python
job = client.generate(tables=[{"name": "journal_entries", "rows": 10000}])
for event in client.jobs.stream(job.id):
    if event["event"] == "progress":
        print(f"Progress: {event['data']['percent']}%")
    elif event["event"] == "complete":
        print("Done!")
        break
```

## Error Handling

```python
from vynfi import VynFi, InsufficientCreditsError, RateLimitError

try:
    job = client.generate(tables=[{"name": "journal_entries", "rows": 1000000}])
except InsufficientCreditsError:
    print("Not enough credits")
except RateLimitError:
    print("Too many requests, retry later")
```

## Configuration

```python
client = VynFi(
    api_key="vf_live_...",
    base_url="https://api.vynfi.com",  # default
    timeout=30.0,                       # seconds
    max_retries=2,                      # retry on 429/5xx
)
```

## License

Apache 2.0
