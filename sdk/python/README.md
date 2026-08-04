# Analytics SDK for Python

A Python SDK for interacting with the Analytics API.

## Installation

Install the SDK from a GitHub release:

```bash
pip install https://github.com/vvaswani/zero-drift/releases/download/sdk-v0.1.0/analytics_sdk-0.1.0-py3-none-any.whl
```

Or install from source:

```bash
pip install -e .
```

## Quick Start

```python
from analytics_sdk import AnalyticsClient

client = AnalyticsClient(api_key="your-api-key")

# Create a property
response = client.analytics.create_property(
    json={
        "name": "My Property",
        "contractID": "550e8400-e29b-41d4-a716-446655440000",
        "timezone": "Europe/Helsinki"
    }
)
property_data = response.json()
property_id = property_data['id']

# Ingest events
client.analytics.ingest_events(
    property_id,
    json={
        "events": [
            {
                "eventName": "page_view",
                "timestamp": "2026-08-04T12:00:00Z",
                "userID": "user123",
                "country": "FI"
            }
        ]
    }
)

# Submit a report query
report_response = client.analytics.submit_report(
    property_id,
    json={
        "dimensions": ["date"],
        "metrics": ["sessions", "pageviews"],
        "dateRange": {
            "startDate": "2026-07-01",
            "endDate": "2026-07-31"
        }
    }
)
report_id = report_response.json()['id']

# Poll for report completion
while True:
    status_response = client.analytics.get_report(property_id, report_id)
    status = status_response.json()['status']
    if status in ['COMPLETED', 'FAILED']:
        break
    # In real code, add delay and timeout handling

# Get results
results_response = client.analytics.get_report_results(property_id, report_id)
results = results_response.json()

client.close()
```

## How the SDK is Generated

The SDK is auto-generated from the OpenAPI specification in `api/analytics-v1.yaml`:

1. **Pydantic Models**: `datamodel-code-generator` reads the OpenAPI spec and generates type-safe Pydantic models in `analytics_sdk/_generated/analytics-v1/models.py`.

2. **Service Wrapper**: A hand-generated service wrapper class (`analytics_sdk/analytics_v1.py`) exposes one method per API operation, each calling `client._request()` with the appropriate HTTP method and path.

3. **Client**: The `AnalyticsClient` class manages API key authentication and provides a unified HTTP interface via `_request()`.

When the Analytics API spec changes:
- Run `python scripts/generate_sdk.py` to regenerate models and service wrapper
- The patch version in `pyproject.toml` is automatically bumped
- A GitHub Actions workflow opens a PR with the regenerated code
- Once merged, the release workflow cuts a new GitHub Release with wheel/sdist

## Error Handling

All methods return `httpx.Response` objects. Check the status code and parse the response body:

```python
response = client.analytics.create_property(json={...})
if response.status_code == 201:
    data = response.json()
    # Handle success
else:
    error = response.json()  # Contains 'code' and 'message'
    # Handle error
```

## Context Manager Usage

Use the client as a context manager to ensure resources are cleaned up:

```python
with AnalyticsClient(api_key="key") as client:
    response = client.analytics.create_property(json={...})
    # Use client...
# Automatically closed
```

## Testing with the Playground

The repo includes a mock API playground that runs the Analytics API locally:

```bash
docker run -p 8000:8000 ghcr.io/vvaswani/zero-drift/analytics-playground:latest
```

Then point your SDK calls to the local playground:

```python
client = AnalyticsClient(api_key="test-key", base_url="http://localhost:8000/analytics")
```

Access the Swagger UI at `http://localhost:8000/analytics/docs`.
