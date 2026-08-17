# Zero Drift

This is an agentic sync system that watches a master source of truth, propagates changes across dependent API references and tooling, then regenerates documentation and release artifacts automatically.

## What this demo shows

- a single source-of-truth API spec in `api/analytics-v1.yaml`
- downstream updates to SDKs, docs, and runnable tooling
- automated detection of spec drift
- regeneration of affected documentation
- release automation for the SDK and playground image
- changelog-oriented release handling as part of the update flow

## Repository layout

- `api/` - canonical OpenAPI source files
- `docs/how-to/` - user-facing guides that must stay aligned with the API
- `sdk/python/` - generated Python SDK and packaging metadata
- `playground/` - local mock API playground for validation and demos
- `scripts/docs_review_agent.py` - agent that checks spec diffs against docs
- `.github/workflows/` - automation for docs, SDK, and playground updates

## End-to-end flow

1. A change lands in the master API source under `api/`.
2. The docs review agent compares the spec diff against `docs/how-to/`.
3. If guidance has drifted, the affected docs are rewritten.
4. The Python SDK is regenerated from the updated OpenAPI spec.
5. The playground container is rebuilt with the refreshed spec.
6. Release workflows publish the updated docs, SDK and playground artifacts.

## Automation

### Docs updates

`.github/workflows/update-docs.yml` runs the docs review agent after API changes and opens a PR if the guides need updates.

### SDK regeneration

`.github/workflows/update-sdk.yml` regenerates the Python SDK from the OpenAPI spec and opens a PR when generated output changes.

### SDK release

`.github/workflows/release-sdk.yml` packages and releases the SDK when the regenerated SDK lands on `main`.

### Playground release

`.github/workflows/release-playground.yml` syncs the API spec into the playground and publishes the updated container image.

## Local validation

### Review the API contract

Inspect `api/analytics-v1.yaml` to see the master contract that drives the rest of the system.

### Run the docs reviewer

```bash
python scripts/docs_review_agent.py
```

The script compares the current API spec diff to the `docs/how-to/` guides and updates them when needed.

### Regenerate the SDK

```bash
cd sdk/python
python scripts/generate_sdk.py
```

### Run the playground

```bash
cd playground
pip install -e .
python -m app.main
```

Then open:

- `http://localhost:8000/analytics/docs`

## Notes

- This repository is designed to demonstrate propagation of changes from a master source file through docs, SDKs, and release automation.
- The playground is a mock environment for validation and should not be treated as a production API.
