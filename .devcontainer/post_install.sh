#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

# Placeholder hook for installing project dependencies
if command -v uv >/dev/null 2>&1; then
  uv sync || true
else
  echo "uv not found; skipping dependency sync"
fi

echo "Devcontainer post-create steps completed."
