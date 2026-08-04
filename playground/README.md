# Analytics API Playground

A mock implementation of the Analytics API for local testing and development.

## Quick Start

### Docker (Recommended)

```bash
docker build -t analytics-playground .
docker run -p 8000:8000 analytics-playground
```

Then visit:
- Swagger UI: http://localhost:8000/analytics/docs
- Root endpoint: http://localhost:8000/

### Local Development

```bash
pip install -e .
python -m app.main
```

## Using the Playground

The playground mounts the Analytics API at `/analytics` and provides:

- **Swagger UI**: `/analytics/docs` — try out API endpoints interactively
- **OpenAPI JSON**: `/analytics/openapi.json` — download the spec
- **Mock Responses**: All endpoints return realistic demo data

## How It Works

### Architecture

1. **FastAPI App**: `app/main.py` mounts the Analytics API sub-app at `/analytics`
2. **Mock Backend**: `app/mock_backend.py` handles all requests
   - First, checks `CANNED_RESPONSES` for hand-authored demo data
   - Falls back to schema-driven response generation if no canned response exists
3. **OpenAPI Spec**: `app/specs/analytics-v1.yaml` is baked into the container at build time

### Canned Responses

The `CANNED_RESPONSES` dict in `mock_backend.py` provides realistic demo responses for key workflows:

- **Properties**: Create and list demo properties
- **Events**: Ingest and retrieve demo events
- **Reports**: Submit report queries, check job status (PENDING → COMPLETED), retrieve results
- **Dashboards**: Create, list, and manage demo dashboards

Everything else falls back to schema-based mocking.

## Regenerating After Spec Changes

When the Analytics API spec changes:

1. The GitHub Actions workflow syncs the updated spec:
   ```bash
   cp api/*.yaml playground/app/specs/
   ```

2. Docker rebuilds the image with:
   ```bash
   docker build -t analytics-playground .
   ```

3. The new image is pushed to `ghcr.io/<repo>/analytics-playground:latest`

The playground doesn't need code changes for spec evolution — it auto-detects specs in `app/specs/` and regenerates FastAPI apps on-the-fly.

## Testing with the SDK

Point the Analytics SDK at the local playground:

```python
from analytics_sdk import AnalyticsClient

client = AnalyticsClient(
    api_key="test-key",
    base_url="http://localhost:8000/analytics"
)

response = client.analytics.create_property(json={
    "name": "Test",
    "contractID": "550e8400-e29b-41d4-a716-446655440001",
})
print(response.json())
```

## Example Requests

### Create a Property

```bash
curl -X POST http://localhost:8000/analytics/properties \
  -H "X-API-Key: test-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Site",
    "contractID": "550e8400-e29b-41d4-a716-446655440001",
    "timezone": "UTC"
  }'
```

### Ingest Events

```bash
curl -X POST http://localhost:8000/analytics/properties/550e8400-e29b-41d4-a716-446655440000/events \
  -H "X-API-Key: test-key" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "eventName": "page_view",
        "timestamp": "2026-08-04T12:00:00Z",
        "userID": "user123",
        "country": "FI"
      }
    ]
  }'
```

### Submit a Report

```bash
curl -X POST http://localhost:8000/analytics/properties/550e8400-e29b-41d4-a716-446655440000/reports \
  -H "X-API-Key: test-key" \
  -H "Content-Type: application/json" \
  -d '{
    "dimensions": ["date"],
    "metrics": ["sessions"],
    "dateRange": {"startDate": "2026-07-01", "endDate": "2026-07-31"}
  }'
```

## Versioning

The playground is published as `:latest` only — no versioned releases. Each spec update triggers a rebuild and push of the latest image to `ghcr.io/vvaswani/zero-drift/analytics-playground:latest`.
