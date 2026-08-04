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
        "datamodel-code-generator",
        "--input", str(spec_path),
        "--input-file-type", "openapi",
        "--output", str(output_file),
        "--target-python-version", "3.9",
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


def bump_patch_version_if_changed() -> bool:
    """Bump patch version if generated SDK code changed."""
    repo_root = Path(__file__).parent.parent.parent
    sdk_dir = repo_root / "sdk" / "python" / "analytics_sdk"

    result = subprocess.run(
        ["git", "diff", "--quiet", "--", str(sdk_dir)],
        capture_output=True,
        cwd=repo_root,
    )

    if result.returncode == 0:
        # No changes
        return False

    pyproject_path = repo_root / "sdk" / "python" / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        pyproject = tomllib.load(f)

    version = pyproject["project"]["version"]
    parts = version.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    new_version = ".".join(parts)

    with open(pyproject_path, "r") as f:
        content = f.read()

    content = re.sub(
        rf'version = "{re.escape(version)}"',
        f'version = "{new_version}"',
        content,
    )

    with open(pyproject_path, "w") as f:
        f.write(content)

    print(f"✓ Bumped version {version} → {new_version}")
    return True


def main():
    """Generate SDK from all OpenAPI specs in api/."""
    repo_root = Path(__file__).parent.parent.parent
    api_dir = repo_root / "api"

    specs = list(api_dir.glob("*.yaml"))
    if not specs:
        print("No OpenAPI specs found in api/")
        sys.exit(1)

    for spec_path in specs:
        service_name = spec_path.stem
        service_module = service_name.replace("-", "_")

        generate_models(spec_path, service_name)
        generate_service_wrapper(spec_path, service_name, service_module)

    bump_patch_version_if_changed()


if __name__ == "__main__":
    main()
