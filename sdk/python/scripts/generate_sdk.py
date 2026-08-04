#!/usr/bin/env python3
"""Generate Analytics SDK from OpenAPI spec."""

import re
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib


def generate_models(spec_path: Path, service_name: str) -> None:
    """Generate Pydantic models from OpenAPI spec using datamodel-code-generator."""
    output_dir = Path(__file__).parent.parent / "analytics_sdk" / "_generated" / service_name
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "models.py"

    cmd = [
        sys.executable, "-m", "datamodel_code_generator",
        "--input", str(spec_path),
        "--input-file-type", "openapi",
        "--output", str(output_file),
        "--target-python-version", "3.10",
    ]

    print(f"Generating models for {service_name}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: Failed to generate models: {result.stderr}")
        sys.exit(1)
    print(f"✓ Generated {output_file}")


def generate_service_wrapper(spec_path: Path, service_name: str, service_module: str) -> None:
    """Generate service wrapper with method stubs for each operation."""
    import yaml

    with open(spec_path) as f:
        spec = yaml.safe_load(f)

    paths = spec.get("paths", {})
    operations = []

    for path_str, methods in paths.items():
        for method, operation in methods.items():
            if method not in ["get", "post", "put", "delete", "patch", "head"]:
                continue
            op_id = operation.get("operationId")
            if not op_id:
                continue
            operations.append({
                "operationId": op_id,
                "method": method.upper(),
                "path": path_str,
            })

    service_code = f'''"""Generated service wrapper for {service_name}."""

from analytics_sdk.client import AnalyticsClient
import httpx


class {to_pascal_case(service_module)}API:
    """API client for {service_name}."""

    def __init__(self, client: AnalyticsClient):
        self.client = client

'''

    for op in operations:
        method_name = to_snake_case(op["operationId"])
        service_code += f'''    def {method_name}(self, **kwargs) -> httpx.Response:
        """Call {op["operationId"]} ({op["method"]} {op["path"]})."""
        return self.client._request("{op["method"]}", "{op["path"]}", **kwargs)

'''

    output_file = Path(__file__).parent.parent / "analytics_sdk" / f"{service_module}.py"
    output_file.write_text(service_code)
    print(f"✓ Generated {output_file}")


def to_pascal_case(snake_str: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(w.capitalize() for w in snake_str.split("_"))


def to_snake_case(camel_str: str) -> str:
    """Convert camelCase to snake_case."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", camel_str)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def sync_version_with_spec(spec_path: Path) -> None:
    """Set SDK version to match API spec version."""
    import yaml

    with open(spec_path) as f:
        spec = yaml.safe_load(f)

    api_version = spec.get("info", {}).get("version", "0.1.0")

    repo_root = Path(__file__).parent.parent.parent.parent
    pyproject_path = repo_root / "sdk" / "python" / "pyproject.toml"

    with open(pyproject_path) as f:
        content = f.read()

    old_version = None
    match = re.search(r'version = "([^"]+)"', content)
    if match:
        old_version = match.group(1)

    content = re.sub(
        r'version = "[^"]+"',
        f'version = "{api_version}"',
        content,
        count=1,
    )

    with open(pyproject_path, "w") as f:
        f.write(content)

    if old_version and old_version != api_version:
        print(f"✓ Synced SDK version {old_version} → {api_version} (from spec)")
    else:
        print(f"✓ SDK version {api_version} (from spec)")


def main():
    """Generate SDK from all OpenAPI specs in api/."""
    repo_root = Path(__file__).parent.parent.parent.parent
    api_dir = repo_root / "api"

    if not api_dir.exists():
        print(f"ERROR: api/ directory not found at {api_dir}")
        print(f"Script location: {Path(__file__)}")
        print(f"Repo root: {repo_root}")
        sys.exit(1)

    specs = list(api_dir.glob("*.yaml"))
    if not specs:
        print(f"No OpenAPI specs found in {api_dir}")
        print(f"Available files: {list(api_dir.iterdir())}")
        sys.exit(1)

    print(f"Found {len(specs)} spec(s): {[s.name for s in specs]}")

    for spec_path in specs:
        service_name = spec_path.stem
        service_module = service_name.replace("-", "_")

        generate_models(spec_path, service_name)
        generate_service_wrapper(spec_path, service_name, service_module)

        sync_version_with_spec(spec_path)


if __name__ == "__main__":
    main()
