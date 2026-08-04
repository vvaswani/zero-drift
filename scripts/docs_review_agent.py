#!/usr/bin/env python3
"""
Docs review agent: checks if an API spec change requires doc updates.

Reads the git diff for api/*.yaml files, compares against docs/how-to/*.md,
and uses OpenRouter to determine if any docs need updating. If yes, updates
the docs directly on disk; the workflow handles commit/PR mechanics.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import httpx


def get_spec_diff() -> str:
    """Get git diff for api/*.yaml files (current vs HEAD~1)."""
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD~1", "--", "api/*.yaml"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.stdout or "(no spec changes detected)"
    except Exception as e:
        return f"(error reading spec diff: {e})"


def read_docs() -> dict[str, str]:
    """Read all markdown files from docs/how-to/."""
    docs = {}
    docs_dir = Path(__file__).parent.parent / "docs" / "how-to"
    if not docs_dir.exists():
        return docs
    for doc_file in docs_dir.glob("*.md"):
        docs[str(doc_file.relative_to(Path(__file__).parent.parent))] = doc_file.read_text()
    return docs


def call_openrouter(spec_diff: str, docs: dict[str, str]) -> dict:
    """Call OpenRouter to analyze spec change and suggest doc updates."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set in environment")
        sys.exit(1)

    docs_text = "\n\n".join(
        f"## File: {path}\n\n{content}" for path, content in docs.items()
    )

    prompt = f"""You are a documentation accuracy reviewer. Analyze the following OpenAPI spec change and determine whether any of the provided how-to guides need updating to stay accurate with the API.

**Spec Change (git diff):**
```
{spec_diff}
```

**Current Documentation:**
{docs_text}

**Your Task:**
1. Compare the spec change against each doc to find any inaccuracies or outdated information.
2. If a doc needs updating, output the EXACT updated content for that doc, preserving all markdown formatting.
3. If multiple docs need updating, provide each one separated by a line with exactly: ===END_FILE===

Output format:
- First line: YES or NO (whether docs need updating)
- If YES, follow with (repeat for each file):
  - A line with exactly: ## File: <path>
  - A blank line
  - The complete updated markdown content
  - A line with exactly: ===END_FILE===
- If NO, just output: NO

The <path> must be a valid path like "docs/how-to/build-analytics-reporting-app.md".

Do NOT include the ## File: line in the actual markdown content. Do NOT include any other text, explanations, or metadata."""

    client = httpx.Client()
    try:
        response = client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
            },
            json={
                #"model": "poolside/laguna-s-2.1:free",
                #"model": "openai/gpt-oss-20b:free",
                "model": "poolside/laguna-xs-2.1",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                "temperature": 0.3,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not content:
            print("ERROR: Empty response from OpenRouter")
            sys.exit(1)

        return content.strip()
    except httpx.HTTPStatusError as e:
        print(f"ERROR: OpenRouter API error: {e.status_code} {e.response.text}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse response as JSON: {e}")
        print(f"Response content: {content}")
        sys.exit(1)
    finally:
        client.close()


def parse_agent_response(response: str) -> tuple[bool, list[tuple[str, str]]]:
    """Parse the agent's text response into (needs_update, [(path, content), ...])."""
    lines = response.split("\n")
    if not lines:
        return False, []

    first_line = lines[0].strip().upper()
    if first_line == "NO":
        return False, []

    if first_line != "YES":
        print(f"WARNING: Expected YES or NO, got: {first_line}")
        return False, []

    # Parse files: look for ## File: <path> header, blank line, content, ===END_FILE===
    files = []
    current_path = None
    current_content = []
    in_file = False
    skip_blank = False

    for line in lines[1:]:
        if line.startswith("## File:"):
            # Extract path from "## File: <path>"
            current_path = line.replace("## File:", "").strip()
            skip_blank = True
            in_file = True
            current_content = []
        elif line == "===END_FILE===":
            if in_file and current_path and current_content:
                content = "\n".join(current_content).strip()
                files.append((current_path, content))
            current_path = None
            current_content = []
            in_file = False
            skip_blank = False
        elif in_file:
            # Skip the first blank line after ## File: header
            if skip_blank and line == "":
                skip_blank = False
            else:
                current_content.append(line)

    return len(files) > 0, files


def apply_updates(files: list[tuple[str, str]]) -> None:
    """Write updated doc content to disk."""
    repo_root = Path(__file__).parent.parent
    for file_path, content in files:
        full_path = repo_root / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        print(f"Updated: {file_path}")


def main():
    """Main entrypoint."""
    spec_diff = get_spec_diff()
    docs = read_docs()

    if not docs:
        print("No documentation files found under docs/how-to/")
        return

    print("Analyzing spec change against documentation...")
    response = call_openrouter(spec_diff, docs)

    needs_update, files = parse_agent_response(response)

    if needs_update:
        print(f"✓ Documentation updates needed")
        apply_updates(files)
    else:
        print(f"✓ No documentation updates needed")


if __name__ == "__main__":
    main()
