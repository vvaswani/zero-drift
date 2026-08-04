"""
FastAPI playground for Analytics API.

Serves Swagger UI docs with mock backend.
Accessible at: /analytics/docs
"""

from pathlib import Path

import yaml
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.mock_backend import MockBackend

APP_DIR = Path(__file__).parent
SPECS_DIR = APP_DIR / "specs"

backends = {}

for spec_file in SPECS_DIR.glob("*.yaml"):
    service_key = spec_file.stem
    backends[service_key] = MockBackend(spec_file, service_key)


def create_service_app(service_name: str, service_key: str) -> FastAPI:
    """Create a FastAPI sub-app for a single service with its own Swagger UI."""
    spec_path = SPECS_DIR / f"{service_key}.yaml"

    if not spec_path.exists():
        raise FileNotFoundError(f"Spec not found: {spec_path}")

    with open(spec_path) as f:
        spec = yaml.safe_load(f)

    # Override servers to point to this service's mount path
    # Ensures Swagger UI's "Try it out" sends requests to the right place
    spec["servers"] = [
        {
            "url": f"/{service_name}",
            "description": "Local playground (mock responses only)",
        }
    ]

    app = FastAPI(
        title=spec.get("info", {}).get("title", f"{service_name} API"),
        version=spec.get("info", {}).get("version", "1.0.0"),
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url=None,
    )

    @app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"], include_in_schema=False)
    async def catch_all(request: Request, path: str):
        method = request.method
        request_path = f"/{path}"
        query_params = dict(request.query_params)

        backend = backends.get(service_key)
        if not backend:
            return JSONResponse(
                {"error": f"No backend for service {service_key}"},
                status_code=500,
            )

        status_code, body = backend.get_mock_response(method, request_path, query_params)
        return JSONResponse(content=body, status_code=status_code)

    # Override openapi() to return the spec with rewritten servers
    def openapi():
        return spec

    app.openapi = openapi

    return app


main_app = FastAPI(
    title="Analytics API Playground",
    version="1.0.0",
    docs_url="/docs",
    openapi_url=None,
)

analytics_app = create_service_app("analytics", "analytics-v1")

main_app.mount("/analytics", analytics_app)


@main_app.get("/")
async def root():
    return {
        "title": "Analytics API Playground",
        "description": "Interactive documentation for the Analytics API",
        "services": {
            "analytics": {"docs": "/analytics/docs", "spec": "/analytics/openapi.json"},
        },
    }


@main_app.get("/docs")
async def main_docs():
    return {
        "message": "Visit the Analytics API docs endpoint",
        "services": {
            "/analytics/docs": "Analytics API v1",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(main_app, host="0.0.0.0", port=8000)
