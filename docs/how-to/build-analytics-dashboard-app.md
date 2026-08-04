# Building an Analytics Dashboard Application

This guide demonstrates how to build an application that uses the Analytics API to create and manage dashboards.

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

For the local playground:

```python
client = AnalyticsClient(
    api_key="test-key",
    base_url="http://localhost:8000/analytics/v1"
)
```

## 2. Understanding Dashboards

A Dashboard is a collection of Widgets, each displaying the results of a Report Query with a specific visualization type.

**Dashboard structure:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440003",
  "name": "Q3 2026 Performance",
  "contractID": "220e8400-e29b-41d4-a716-446655440001",
  "widgets": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440004",
      "title": "Daily Sessions",
      "reportQuery": { /* ReportQuery object */ },
      "visualization": "line"
    }
  ],
  "createdAt": "2026-08-04T10:30:00Z",
  "updatedAt": "2026-08-04T10:30:00Z"
}
```

**Visualization types:**
- `table`: Display results in a tabular format
- `line`: Line chart (best for time-series data)
- `bar`: Bar chart (good for comparisons)
- `stacked`: Stacked bar chart (good for comparing parts of a whole)

## 3. Creating a Dashboard

Create a new dashboard with one or more widgets:

```python
response = client.analytics.create_dashboard(
    json={
        "name": "Website Performance Dashboard",
        "contractID": "550e8400-e29b-41d4-a716-446655440000",
        "widgets": [
            {
                "title": "Daily Active Users",
                "reportQuery": {
                    "dimensions": ["date"],
                    "metrics": ["users"],
                    "dateRange": {
                        "startDate": "2026-07-01",
                        "endDate": "2026-07-31"
                    }
                },
                "visualization": "line"
            },
            {
                "title": "Sessions by Country",
                "reportQuery": {
                    "dimensions": ["country"],
                    "metrics": ["sessions"],
                    "dateRange": {
                        "startDate": "2026-07-01",
                        "endDate": "2026-07-31"
                    }
                },
                "visualization": "bar"
            }
        ]
    }
)

if response.status_code == 201:
    dashboard = response.json()
    dashboard_id = dashboard['id']
    print(f"Dashboard created: {dashboard_id}")
    print(f"Widgets: {len(dashboard['widgets'])}")
else:
    error = response.json()
    print(f"Error: {error['message']}")
```

**Dashboard fields:**
- `name` (required): Human-readable dashboard name
- `contractID` (required): Your billing contract ID
- `widgets` (required): Array of at least 1 widget

**Widget fields:**
- `title` (required): Widget title (displayed on dashboard)
- `reportQuery` (required): ReportQuery object (see reporting guide for details)
- `visualization` (optional): "table", "line", "bar", or "stacked" (defaults to "table")

## 4. Listing Dashboards

Retrieve all dashboards in your contract:

```python
response = client.analytics.list_dashboards(
    params={
        "limit": 50,
        "cursor": None
    }
)

if response.status_code == 200:
    result = response.json()
    print(f"Total dashboards: {len(result['data'])}")
    
    for dashboard in result['data']:
        print(f"  {dashboard['name']} ({dashboard['id']})")
        print(f"    Widgets: {len(dashboard['widgets'])}")
        if result.get('cursor'):
            print(f"    More results available")
else:
    error = response.json()
    print(f"Error: {error['message']}")
```

**Response:**
```json
{
  "data": [ /* array of Dashboards */ ],
  "cursor": "eyJvZmZzZXQiOiA1MH0="
}
```

Use the `cursor` field for pagination if there are more results.

## 5. Getting Dashboard Details

Retrieve a specific dashboard:

```python
dashboard_id = "770e8400-e29b-41d4-a716-446655440003"

response = client.analytics.get_dashboard(dashboard_id)

if response.status_code == 200:
    dashboard = response.json()
    print(f"Dashboard: {dashboard['name']}")
    print(f"Contract: {dashboard['contractID']}")
    print(f"Created: {dashboard['createdAt']}")
    
    for widget in dashboard['widgets']:
        print(f"  - {widget['title']} ({widget['visualization']})")
else:
    error = response.json()
    print(f"Error: {error['message']}")
```

## 6. Updating a Dashboard

Modify dashboard name and/or widgets (PATCH operation):

```python
dashboard_id = "770e8400-e29b-41d4-a716-446655440003"

response = client.analytics.update_dashboard(
    dashboard_id,
    json={
        "name": "Q3 2026 Updated Performance",
        "widgets": [
            {
                "title": "Daily Active Users",
                "reportQuery": {
                    "dimensions": ["date"],
                    "metrics": ["users"],
                    "dateRange": {
                        "startDate": "2026-07-01",
                        "endDate": "2026-07-31"
                    }
                },
                "visualization": "line"
            },
            {
                "title": "Bounce Rate by Country",
                "reportQuery": {
                    "dimensions": ["country"],
                    "metrics": ["bounceRate"],
                    "dateRange": {
                        "startDate": "2026-07-01",
                        "endDate": "2026-07-31"
                    }
                },
                "visualization": "bar"
            },
            {
                "title": "Event Timeline",
                "reportQuery": {
                    "dimensions": ["date"],
                    "metrics": ["eventCount"],
                    "dateRange": {
                        "startDate": "2026-07-01",
                        "endDate": "2026-07-31"
                    }
                },
                "visualization": "table"
            }
        ]
    }
)

if response.status_code == 200:
    dashboard = response.json()
    print(f"Dashboard updated: {dashboard['id']}")
    print(f"New widget count: {len(dashboard['widgets'])}")
else:
    error = response.json()
    print(f"Error: {error['message']}")
```

**Update behavior:**
- Omit `name` to keep the existing name
- Omit `widgets` to keep the existing widgets
- When providing `widgets`, the entire widget list is replaced (not merged)

## 7. Deleting a Dashboard

Remove a dashboard:

```python
dashboard_id = "770e8400-e29b-41d4-a716-446655440003"

response = client.analytics.delete_dashboard(dashboard_id)

if response.status_code == 204:
    print("Dashboard deleted successfully")
else:
    error = response.json()
    print(f"Error: {error['message']}")
```

**Note:** HTTP 204 means success with no response body.

## 8. Error Handling

Handle common dashboard API errors:

```python
response = client.analytics.get_dashboard(dashboard_id)

if response.status_code >= 400:
    error = response.json()
    code = error['code']
    message = error['message']
    
    if response.status_code == 400:
        print(f"Bad Request: {message}")  # Invalid widget/query
    elif response.status_code == 401:
        print(f"Unauthorized: check your API key")
    elif response.status_code == 404:
        print(f"Dashboard not found: {message}")
    elif response.status_code == 429:
        print(f"Rate Limited: wait before retrying")
    elif response.status_code == 500:
        print(f"Server Error: {message}")
```

## 9. Testing with the Playground

Run the mock Analytics API locally:

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

Visit `http://localhost:8000/analytics/docs` to try dashboard endpoints interactively.

## Complete End-to-End Example

```python
from analytics_sdk import AnalyticsClient

client = AnalyticsClient(api_key="your-api-key")

try:
    # Step 1: Create a dashboard with multiple widgets
    print("1. Creating dashboard...")
    resp = client.analytics.create_dashboard(
        json={
            "name": "Monthly Analytics Dashboard",
            "contractID": "550e8400-e29b-41d4-a716-446655440000",
            "widgets": [
                {
                    "title": "Sessions Over Time",
                    "reportQuery": {
                        "dimensions": ["date"],
                        "metrics": ["sessions"],
                        "dateRange": {
                            "startDate": "2026-07-01",
                            "endDate": "2026-07-31"
                        }
                    },
                    "visualization": "line"
                },
                {
                    "title": "Top Countries",
                    "reportQuery": {
                        "dimensions": ["country"],
                        "metrics": ["sessions", "users"],
                        "dateRange": {
                            "startDate": "2026-07-01",
                            "endDate": "2026-07-31"
                        }
                    },
                    "visualization": "bar"
                },
                {
                    "title": "Device Breakdown",
                    "reportQuery": {
                        "dimensions": ["deviceType"],
                        "metrics": ["sessions"],
                        "dateRange": {
                            "startDate": "2026-07-01",
                            "endDate": "2026-07-31"
                        }
                    },
                    "visualization": "bar"
                }
            ]
        }
    )
    
    dashboard = resp.json()
    dashboard_id = dashboard['id']
    print(f"   Dashboard created: {dashboard_id}")
    print(f"   Widgets: {len(dashboard['widgets'])}")

    # Step 2: List all dashboards
    print("\n2. Listing all dashboards...")
    resp = client.analytics.list_dashboards()
    dashboards = resp.json()['data']
    print(f"   Total dashboards: {len(dashboards)}")
    for d in dashboards:
        print(f"     - {d['name']} ({len(d['widgets'])} widgets)")

    # Step 3: Get dashboard details
    print(f"\n3. Getting dashboard details...")
    resp = client.analytics.get_dashboard(dashboard_id)
    dashboard = resp.json()
    print(f"   Name: {dashboard['name']}")
    print(f"   Created: {dashboard['createdAt']}")
    print(f"   Widgets:")
    for widget in dashboard['widgets']:
        print(f"     - {widget['title']} ({widget['visualization']})")

    # Step 4: Update dashboard (add a new widget)
    print(f"\n4. Updating dashboard...")
    resp = client.analytics.update_dashboard(
        dashboard_id,
        json={
            "widgets": [
                {
                    "title": "Sessions Over Time",
                    "reportQuery": {
                        "dimensions": ["date"],
                        "metrics": ["sessions"],
                        "dateRange": {
                            "startDate": "2026-07-01",
                            "endDate": "2026-07-31"
                        }
                    },
                    "visualization": "line"
                },
                {
                    "title": "Top Countries",
                    "reportQuery": {
                        "dimensions": ["country"],
                        "metrics": ["sessions", "users"],
                        "dateRange": {
                            "startDate": "2026-07-01",
                            "endDate": "2026-07-31"
                        }
                    },
                    "visualization": "bar"
                },
                {
                    "title": "Device Breakdown",
                    "reportQuery": {
                        "dimensions": ["deviceType"],
                        "metrics": ["sessions"],
                        "dateRange": {
                            "startDate": "2026-07-01",
                            "endDate": "2026-07-31"
                        }
                    },
                    "visualization": "bar"
                },
                {
                    "title": "Pageviews by Path",
                    "reportQuery": {
                        "dimensions": ["pagePath"],
                        "metrics": ["pageviews"],
                        "dateRange": {
                            "startDate": "2026-07-01",
                            "endDate": "2026-07-31"
                        },
                        "limit": 10
                    },
                    "visualization": "table"
                }
            ]
        }
    )
    
    dashboard = resp.json()
    print(f"   Dashboard updated")
    print(f"   New widget count: {len(dashboard['widgets'])}")

    # Step 5: Delete dashboard
    print(f"\n5. Deleting dashboard...")
    resp = client.analytics.delete_dashboard(dashboard_id)
    if resp.status_code == 204:
        print(f"   Dashboard deleted")
    else:
        print(f"   Error: {resp.json()['message']}")

finally:
    client.close()
```

## Common Patterns

### Dashboard Refresh Pattern

Periodically fetch and display dashboard data:

```python
import time

dashboard_id = "770e8400-e29b-41d4-a716-446655440003"

for iteration in range(24):  # Refresh every minute for 24 minutes
    resp = client.analytics.get_dashboard(dashboard_id)
    dashboard = resp.json()
    
    print(f"\n=== Dashboard Refresh {iteration + 1} ===")
    print(f"Last updated: {dashboard['updatedAt']}")
    print(f"Widgets: {len(dashboard['widgets'])}")
    
    time.sleep(60)
```

### Dashboard as Template

Create a template dashboard and clone it for different date ranges:

```python
def create_weekly_dashboard(week_start_date, week_end_date):
    """Create a dashboard for a specific week."""
    resp = client.analytics.create_dashboard(
        json={
            "name": f"Week {week_start_date}",
            "contractID": "550e8400-e29b-41d4-a716-446655440000",
            "widgets": [
                {
                    "title": "Weekly Performance",
                    "reportQuery": {
                        "dimensions": ["date"],
                        "metrics": ["sessions", "users", "pageviews"],
                        "dateRange": {
                            "startDate": week_start_date,
                            "endDate": week_end_date
                        }
                    },
                    "visualization": "line"
                }
            ]
        }
    )
    return resp.json()['id']

# Create dashboards for 4 weeks
dashboard_ids = [
    create_weekly_dashboard("2026-07-01", "2026-07-07"),
    create_weekly_dashboard("2026-07-08", "2026-07-14"),
    create_weekly_dashboard("2026-07-15", "2026-07-21"),
    create_weekly_dashboard("2026-07-22", "2026-07-31"),
]

print(f"Created {len(dashboard_ids)} weekly dashboards")
```

## Next Steps

- Explore [build-analytics-reporting-app.md](build-analytics-reporting-app.md) for event ingestion and ad-hoc reports
- Check the [Analytics API spec](../api/analytics-v1.yaml) for complete API reference
- Try the playground at `http://localhost:8000/analytics/docs`