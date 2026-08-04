"""Mock backend that generates canned responses from OpenAPI specs."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

import yaml


CANNED_RESPONSES = {
    "analytics-v1": {
        "/properties": {
            "POST": {
                "status": 201,
                "body": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Demo Property",
                    "contractID": "220e8400-e29b-41d4-a716-446655440001",
                    "timezone": "Europe/Helsinki",
                    "createdAt": "2026-08-04T10:00:00Z",
                    "updatedAt": "2026-08-04T10:00:00Z",
                }
            },
            "GET": {
                "status": 200,
                "body": {
                    "data": [
                        {
                            "id": "550e8400-e29b-41d4-a716-446655440000",
                            "name": "Demo Property",
                            "contractID": "220e8400-e29b-41d4-a716-446655440001",
                            "timezone": "Europe/Helsinki",
                            "createdAt": "2026-08-04T10:00:00Z",
                            "updatedAt": "2026-08-04T10:00:00Z",
                        }
                    ]
                }
            }
        },
        "/properties/550e8400-e29b-41d4-a716-446655440000/events": {
            "POST": {
                "status": 202,
                "body": {
                    "accepted": 5
                }
            },
            "GET": {
                "status": 200,
                "body": {
                    "data": [
                        {
                            "id": str(uuid4()),
                            "eventName": "page_view",
                            "timestamp": "2026-08-04T12:30:00Z",
                            "userID": "user123",
                            "country": "FI",
                            "deviceType": "desktop",
                            "pagePath": "/pricing",
                        },
                        {
                            "id": str(uuid4()),
                            "eventName": "session_start",
                            "timestamp": "2026-08-04T12:00:00Z",
                            "userID": "user456",
                            "country": "SE",
                            "deviceType": "mobile",
                            "pagePath": "/",
                        }
                    ]
                }
            }
        },
        "/properties/550e8400-e29b-41d4-a716-446655440000/reports": {
            "POST": {
                "status": 201,
                "body": {
                    "id": "660e8400-e29b-41d4-a716-446655440002",
                    "propertyID": "550e8400-e29b-41d4-a716-446655440000",
                    "status": "PENDING",
                    "query": {
                        "dimensions": ["date"],
                        "metrics": ["sessions"],
                        "dateRange": {
                            "startDate": "2026-07-01",
                            "endDate": "2026-07-31"
                        }
                    },
                    "createdAt": "2026-08-04T12:00:00Z",
                    "updatedAt": "2026-08-04T12:00:00Z",
                }
            },
            "GET": {
                "status": 200,
                "body": {
                    "data": [
                        {
                            "id": "660e8400-e29b-41d4-a716-446655440002",
                            "propertyID": "550e8400-e29b-41d4-a716-446655440000",
                            "status": "COMPLETED",
                            "query": {
                                "dimensions": ["date"],
                                "metrics": ["sessions"],
                                "dateRange": {
                                    "startDate": "2026-07-01",
                                    "endDate": "2026-07-31"
                                }
                            },
                            "createdAt": "2026-08-04T11:00:00Z",
                            "updatedAt": "2026-08-04T12:05:00Z",
                            "completedAt": "2026-08-04T12:05:00Z",
                        }
                    ]
                }
            }
        },
        "/properties/550e8400-e29b-41d4-a716-446655440000/reports/660e8400-e29b-41d4-a716-446655440002": {
            "GET": {
                "status": 200,
                "body": {
                    "id": "660e8400-e29b-41d4-a716-446655440002",
                    "propertyID": "550e8400-e29b-41d4-a716-446655440000",
                    "status": "COMPLETED",
                    "query": {
                        "dimensions": ["date"],
                        "metrics": ["sessions"],
                        "dateRange": {
                            "startDate": "2026-07-01",
                            "endDate": "2026-07-31"
                        }
                    },
                    "createdAt": "2026-08-04T11:00:00Z",
                    "updatedAt": "2026-08-04T12:05:00Z",
                    "completedAt": "2026-08-04T12:05:00Z",
                }
            }
        },
        "/properties/550e8400-e29b-41d4-a716-446655440000/reports/660e8400-e29b-41d4-a716-446655440002/results": {
            "GET": {
                "status": 200,
                "body": {
                    "reportID": "660e8400-e29b-41d4-a716-446655440002",
                    "rows": [
                        {
                            "dimensions": {"date": "2026-07-01"},
                            "metrics": {"sessions": 42.0}
                        },
                        {
                            "dimensions": {"date": "2026-07-02"},
                            "metrics": {"sessions": 51.0}
                        },
                        {
                            "dimensions": {"date": "2026-07-03"},
                            "metrics": {"sessions": 38.0}
                        }
                    ],
                    "totalRows": 31
                }
            }
        },
        "/dashboards": {
            "POST": {
                "status": 201,
                "body": {
                    "id": "770e8400-e29b-41d4-a716-446655440003",
                    "name": "Demo Dashboard",
                    "contractID": "220e8400-e29b-41d4-a716-446655440001",
                    "widgets": [
                        {
                            "id": "880e8400-e29b-41d4-a716-446655440004",
                            "title": "Daily Sessions",
                            "reportQuery": {
                                "dimensions": ["date"],
                                "metrics": ["sessions"],
                                "dateRange": {
                                    "startDate": "2026-07-01",
                                    "endDate": "2026-07-31"
                                }
                            },
                            "visualization": "line"
                        }
                    ],
                    "createdAt": "2026-08-04T10:30:00Z",
                    "updatedAt": "2026-08-04T10:30:00Z",
                }
            },
            "GET": {
                "status": 200,
                "body": {
                    "data": [
                        {
                            "id": "770e8400-e29b-41d4-a716-446655440003",
                            "name": "Demo Dashboard",
                            "contractID": "220e8400-e29b-41d4-a716-446655440001",
                            "widgets": [
                                {
                                    "id": "880e8400-e29b-41d4-a716-446655440004",
                                    "title": "Daily Sessions",
                                    "reportQuery": {
                                        "dimensions": ["date"],
                                        "metrics": ["sessions"],
                                        "dateRange": {
                                            "startDate": "2026-07-01",
                                            "endDate": "2026-07-31"
                                        }
                                    },
                                    "visualization": "line"
                                }
                            ],
                            "createdAt": "2026-08-04T10:30:00Z",
                            "updatedAt": "2026-08-04T10:30:00Z",
                        }
                    ]
                }
            }
        }
    }
}


class MockBackend:
    """Mock backend for an OpenAPI service."""

    def __init__(self, spec_path: Path, service_key: str):
        self.spec_path = spec_path
        self.service_key = service_key
        with open(spec_path) as f:
            self.spec = yaml.safe_load(f)

    def get_mock_response(self, method: str, path: str, query_params: dict) -> tuple[int, dict]:
        """Return a mock response for the given request."""
        canned = CANNED_RESPONSES.get(self.service_key, {}).get(path, {}).get(method)
        if canned:
            return canned["status"], canned["body"]

        return self._generate_from_schema(method, path, query_params)

    def _generate_from_schema(self, method: str, path: str, query_params: dict) -> tuple[int, dict]:
        """Generate a response from the OpenAPI schema as fallback."""
        paths = self.spec.get("paths", {})
        path_spec = paths.get(path, {})
        operation = path_spec.get(method.lower(), {})

        responses = operation.get("responses", {})
        for status_code in ["200", "201", "202"]:
            if status_code in responses:
                response_spec = responses[status_code]
                content = response_spec.get("content", {})
                json_content = content.get("application/json", {})
                schema = json_content.get("schema", {})

                if "$ref" in schema:
                    schema = self._resolve_ref(schema["$ref"])

                return int(status_code), {"message": f"Mock response for {method} {path}"}

        return 500, {"error": "No response schema found"}

    def _resolve_ref(self, ref: str) -> dict:
        """Resolve a JSON schema $ref."""
        if not ref.startswith("#/components/schemas/"):
            return {}

        schema_name = ref.split("/")[-1]
        schemas = self.spec.get("components", {}).get("schemas", {})
        return schemas.get(schema_name, {})
