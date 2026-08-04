# Building an Analytics Reporting Application

This guide demonstrates how to build an application that uses the Analytics API to ingest events and generate reports.

## Prerequisites

- Python 3.9+
- The `analytics-sdk` package installed
- An API key for the Analytics API
- A contractID from your Analytics account

## 1. Authentication

All Analytics API requests require an `X-API-Key` header. The SDK handles this automatically:

```python
from analytics_sdk import AnalyticsClient

client = AnalyticsClient(api_key="your-api-key-here")
```

The API key must be passed to every request. If you're using the local playground:

```python
client = AnalyticsClient(
    api_key="test-key",
    base_url="http://localhost:8000/analytics"
)
```

## 2. Creating a Property

Properties are the root resource in Analytics API. Each property represents a website, app, or data stream you want to track.

```python
response = client.analytics.create_property(
    json={
        "name": "My E-commerce Site",
        "contractID": "550e8400-e29b-41d4-a716-446655440000",
        "timezone": "Europe/Helsinki"
    }
)

if response.status_code == 201:
    property_data = response.json()
    property_id = property_data['id']
    print(f"Created property: {property_id}")
else:
    error = response.json()
    print(f"Error: {error['code']} - {error['message']}")
```

**Required fields:**
- `name`: Human-readable name for the property
- `contractID`: Your billing/permissions contract ID (UUID format)
- `timezone` (optional): IANA timezone name (defaults to UTC)

**Response:** Returns the created Property object with `id`, `createdAt`, `updatedAt`.

## 3. Ingesting Events

Events represent user actions: page views, clicks, form submissions, purchases, etc. Send events to your property using the event ingestion API.

```python
response = client.analytics.ingest_events(
    property_id,
    json={
        "events": [
            {
                "eventName": "page_view",
                "timestamp": "2026-08-04T12:30:45Z",
                "userID": "user-123",
                "sessionID": "session-456",
                "country": "FI",
                "deviceType": "desktop",
                "pagePath": "/checkout",
                "properties": {
                    "total_value": "99.99",
                    "currency": "EUR"
                }
            },
            {
                "eventName": "purchase",
                "timestamp": "2026-08-04T12:31:00Z",
                "userID": "user-123",
                "sessionID": "session-456",
                "country": "FI",
                "deviceType": "desktop",
                "properties": {
                    "order_id": "order-789",
                    "amount": "99.99"
                }
            }
        ]
    }
)

if response.status_code == 202:
    result = response.json()
    print(f"Accepted {result['accepted']} events for ingestion")
else:
    error = response.json()
    print(f"Error: {error['message']}")
```

**Event fields:**
- `eventName` (required): Name of the event (e.g., "page_view", "purchase")
- `timestamp` (required): RFC 3339 timestamp when the event occurred
- `userID` (optional): End-user or session identifier
- `sessionID` (optional): Session identifier
- `country` (optional): ISO 3166-1 alpha-2 country code (e.g., "US", "FI")
- `deviceType` (optional): "desktop", "mobile", or "tablet"
- `pagePath` (optional): Page path (e.g., "/pricing")
- `properties` (optional): Custom key-value properties (string values only)

**Response:** Returns `{ "accepted": <count> }` — the number of events queued for ingestion (HTTP 202).

## 4. Submitting a Report Query

Reports analyze your events by dimensions and metrics. Submit a query to generate a new report job.

```python
response = client.analytics.submit_report(
    property_id,
    json={
        "dimensions": ["date", "country"],
        "metrics": ["sessions", "pageviews", "users"],
        "dateRange": {
            "startDate": "2026-07-01",
            "endDate": "2026-07-31"
        },
        "filters": [
            {
                "dimension": "country",
                "in": ["FI", "SE", "NO"]
            }
        ]
    }
)

if response.status_code == 201:
    report_job = response.json()
    report_id = report_job['id']
    print(f"Report job created: {report_id}, status: {report_job['status']}")
else:
    error = response.json()
    print(f"Error: {error['message']}")
```

**Report Query fields:**
- `dimensions` (required): List of dimensions to group by. Options: "date", "country", "deviceType", "pagePath", "eventName"
- `metrics` (required): List of metrics to aggregate. Options: "sessions", "pageviews", "users", "bounceRate", "eventCount"
- `dateRange` (required): Object with `startDate` and `endDate` (YYYY-MM-DD format)
- `filters` (optional): List of filters to apply. Each filter has:
  - `dimension`: The dimension to filter on
  - `eq`: Exact match value (mutually exclusive with `in`)
  - `in`: Array of values to match any of
- `limit` (optional): Maximum rows to return (default: 1000)

**Response:** Returns a ReportJob with `status: "PENDING"`. The job runs asynchronously.

## 5. Polling Report Status

Reports are generated asynchronously. Poll the job status until it completes.

```python
import time

max_attempts = 60
attempt = 0

while attempt < max_attempts:
    response = client.analytics.get_report(property_id, report_id)
    
    if response.status_code != 200:
        print(f"Error fetching report: {response.json()['message']}")
        break
    
    job = response.json()
    status = job['status']
    
    if status == "COMPLETED":
        print(f"Report completed after {attempt} polls")
        break
    elif status == "FAILED":
        error_msg = job.get('errorMessage', 'Unknown error')
        print(f"Report failed: {error_msg}")
        break
    elif status in ["PENDING", "RUNNING"]:
        print(f"Report status: {status}, waiting...")
        time.sleep(2)
        attempt += 1
    else:
        print(f"Unknown status: {status}")
        break
else:
    print("Report generation timed out")
```

**Job Statuses:**
- `PENDING`: Report queued, not yet started
- `RUNNING`: Report generation in progress
- `COMPLETED`: Report ready to retrieve results
- `FAILED`: Report generation failed (check `errorMessage`)

## 6. Retrieving Report Results

Once a report is COMPLETED, fetch the actual results.

```python
response = client.analytics.get_report_results(
    property_id,
    report_id,
    params={"limit": 100}  # Paginate if needed
)

if response.status_code == 200:
    result = response.json()
    print(f"Total rows: {result['totalRows']}")
    
    for row in result['rows']:
        dimensions = row['dimensions']
        metrics = row['metrics']
        print(f"{dimensions['date']} ({dimensions['country']}): {metrics['sessions']} sessions")
    
    # Check for more results
    if result.get('cursor'):
        print(f"More results available. Next cursor: {result['cursor']}")
else:
    error = response.json()
    print(f"Error: {error['message']}")
```

**Response structure:**
```json
{
  "reportID": "660e8400-e29b-41d4-a716-446655440002",
  "rows": [
    {
      "dimensions": {
        "date": "2026-07-01",
        "country": "FI"
      },
      "metrics": {
        "sessions": 125.0,
        "pageviews": 342.0,
        "users": 98.0
      }
    }
  ],
  "totalRows": 153,
  "cursor": "eyJvZmZzZXQiOiAxMDB9"
}
```

## 7. Error Handling

The API returns standardized error responses:

```python
if response.status_code >= 400:
    error = response.json()
    code = error['code']
    message = error['message']
    
    if response.status_code == 400:
        print(f"Bad Request: {message}")  # Invalid parameters
    elif response.status_code == 401:
        print(f"Unauthorized: check your API key")
    elif response.status_code == 404:
        print(f"Not Found: {message}")  # Property/report doesn't exist
    elif response.status_code == 429:
        print(f"Rate Limited: wait before retrying")
    elif response.status_code == 500:
        print(f"Server Error: {message}")
```

**Common error codes:**
- `INVALID_REQUEST`: Missing or malformed required fields
- `UNAUTHORIZED`: API key missing or invalid
- `NOT_FOUND`: Resource (property, report) doesn't exist
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server-side error

## 8. Testing with the Playground

The repo includes a mock Analytics API playground for local testing:

```bash
docker run -p 8000:8000 ghcr.io/vvaswani/zero-drift/analytics-playground:latest
```

Then in your code:

```python
client = AnalyticsClient(
    api_key="test-key",
    base_url="http://localhost:8000/analytics"
)
```

Visit the Swagger UI at `http://localhost:8000/analytics/docs` to explore endpoints interactively.

## Complete End-to-End Example

```python
from analytics_sdk import AnalyticsClient
import time
import json
from datetime import datetime

# Initialize client
client = AnalyticsClient(api_key="your-api-key")

try:
    # Step 1: Create a property
    print("1. Creating property...")
    resp = client.analytics.create_property(
        json={
            "name": "Demo Analytics Site",
            "contractID": "550e8400-e29b-41d4-a716-446655440000",
            "timezone": "Europe/Helsinki"
        }
    )
    property_id = resp.json()['id']
    print(f"   Property created: {property_id}")

    # Step 2: Ingest some events
    print("2. Ingesting events...")
    resp = client.analytics.ingest_events(
        property_id,
        json={
            "events": [
                {
                    "eventName": "page_view",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "userID": "user-1",
                    "country": "FI",
                    "pagePath": "/",
                },
                {
                    "eventName": "page_view",
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "userID": "user-2",
                    "country": "SE",
                    "pagePath": "/pricing",
                }
            ]
        }
    )
    print(f"   Accepted {resp.json()['accepted']} events")

    # Step 3: Submit a report query
    print("3. Submitting report query...")
    resp = client.analytics.submit_report(
        property_id,
        json={
            "dimensions": ["country"],
            "metrics": ["sessions", "users"],
            "dateRange": {
                "startDate": "2026-08-01",
                "endDate": "2026-08-04"
            }
        }
    )
    report_id = resp.json()['id']
    print(f"   Report job created: {report_id}")

    # Step 4: Wait for report completion
    print("4. Waiting for report completion...")
    for attempt in range(60):
        resp = client.analytics.get_report(property_id, report_id)
        status = resp.json()['status']
        
        if status == "COMPLETED":
            print(f"   Report completed!")
            break
        else:
            print(f"   Status: {status}")
            time.sleep(1)

    # Step 5: Fetch and display results
    print("5. Fetching report results...")
    resp = client.analytics.get_report_results(property_id, report_id)
    result = resp.json()
    
    print(f"\n   Report Results (Total: {result['totalRows']} rows)")
    print("   " + "=" * 50)
    for row in result['rows']:
        dims = row['dimensions']
        metrics = row['metrics']
        print(f"   {dims.get('country', 'N/A')}: {metrics['sessions']} sessions, {metrics['users']} users")

finally:
    client.close()
```

## Next Steps

- Explore [build-analytics-dashboard-app.md](build-analytics-dashboard-app.md) for dashboard management
- Check the [Analytics API spec](../api/analytics-v1.yaml) for complete reference
- Try the playground locally at `http://localhost:8000/analytics/docs`
