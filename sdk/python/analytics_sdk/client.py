"""Analytics API client."""

from typing import TYPE_CHECKING, Optional

import httpx

if TYPE_CHECKING:
    from analytics_sdk.analytics_v1 import AnalyticsV1API


class AnalyticsClient:
    """
    Client for the Analytics API.

    Provides access to the Analytics API with automatic API key management.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.example.com/analytics/v1",
    ):
        self.api_key = api_key
        self.base_url = base_url
        self._http_client = httpx.Client()
        self._analytics_v1: Optional["AnalyticsV1API"] = None

    @property
    def analytics(self) -> "AnalyticsV1API":
        """Get the Analytics API client."""
        if self._analytics_v1 is None:
            from analytics_sdk.analytics_v1 import AnalyticsV1API

            self._analytics_v1 = AnalyticsV1API(self)
        return self._analytics_v1

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers with API key authorization."""
        return {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def _request(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> httpx.Response:
        """Make an authenticated HTTP request."""
        url = f"{self.base_url}{path}"
        headers = self._get_headers()
        kwargs.setdefault("headers", {}).update(headers)
        return self._http_client.request(method, url, **kwargs)

    def close(self) -> None:
        """Close the client and release resources."""
        self._http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
