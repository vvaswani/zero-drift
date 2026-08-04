"""Generated service wrapper for analytics-v1."""

from analytics_sdk.client import AnalyticsClient
import httpx


class AnalyticsV1API:
    """API client for analytics-v1."""

    def __init__(self, client: AnalyticsClient):
        self.client = client

    def create_property(self, **kwargs) -> httpx.Response:
        """Call createProperty (POST /properties)."""
        return self.client._request("POST", "/properties", **kwargs)

    def list_properties(self, **kwargs) -> httpx.Response:
        """Call listProperties (GET /properties)."""
        return self.client._request("GET", "/properties", **kwargs)

    def get_property(self, **kwargs) -> httpx.Response:
        """Call getProperty (GET /properties/{propertyID})."""
        return self.client._request("GET", "/properties/{propertyID}", **kwargs)

    def ingest_events(self, **kwargs) -> httpx.Response:
        """Call ingestEvents (POST /properties/{propertyID}/events)."""
        return self.client._request("POST", "/properties/{propertyID}/events", **kwargs)

    def list_events(self, **kwargs) -> httpx.Response:
        """Call listEvents (GET /properties/{propertyID}/events)."""
        return self.client._request("GET", "/properties/{propertyID}/events", **kwargs)

    def submit_report(self, **kwargs) -> httpx.Response:
        """Call submitReport (POST /properties/{propertyID}/reports)."""
        return self.client._request("POST", "/properties/{propertyID}/reports", **kwargs)

    def list_reports(self, **kwargs) -> httpx.Response:
        """Call listReports (GET /properties/{propertyID}/reports)."""
        return self.client._request("GET", "/properties/{propertyID}/reports", **kwargs)

    def get_report(self, **kwargs) -> httpx.Response:
        """Call getReport (GET /properties/{propertyID}/reports/{reportID})."""
        return self.client._request("GET", "/properties/{propertyID}/reports/{reportID}", **kwargs)

    def get_report_results(self, **kwargs) -> httpx.Response:
        """Call getReportResults (GET /properties/{propertyID}/reports/{reportID}/results)."""
        return self.client._request("GET", "/properties/{propertyID}/reports/{reportID}/results", **kwargs)

    def create_dashboard(self, **kwargs) -> httpx.Response:
        """Call createDashboard (POST /dashboards)."""
        return self.client._request("POST", "/dashboards", **kwargs)

    def list_dashboards(self, **kwargs) -> httpx.Response:
        """Call listDashboards (GET /dashboards)."""
        return self.client._request("GET", "/dashboards", **kwargs)

    def get_dashboard(self, **kwargs) -> httpx.Response:
        """Call getDashboard (GET /dashboards/{dashboardID})."""
        return self.client._request("GET", "/dashboards/{dashboardID}", **kwargs)

    def update_dashboard(self, **kwargs) -> httpx.Response:
        """Call updateDashboard (PATCH /dashboards/{dashboardID})."""
        return self.client._request("PATCH", "/dashboards/{dashboardID}", **kwargs)

    def delete_dashboard(self, **kwargs) -> httpx.Response:
        """Call deleteDashboard (DELETE /dashboards/{dashboardID})."""
        return self.client._request("DELETE", "/dashboards/{dashboardID}", **kwargs)

