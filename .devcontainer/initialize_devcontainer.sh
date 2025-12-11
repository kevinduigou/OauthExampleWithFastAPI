#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PROJECT_NAME=${PROJECT_NAME:-mynicegui}
USERNAME=${USER:-vscode}

# Build the base image used by the main devcontainer Dockerfile
DOCKER_BUILDKIT=1 docker build \
  -f "${SCRIPT_DIR}/base.Dockerfile" \
  --build-arg PROJECT_NAME="${PROJECT_NAME}" \
  --build-arg USERNAME="${USERNAME}" \
  -t "${PROJECT_NAME}:base" \
  "${SCRIPT_DIR}"
