#!/bin/bash
set -e

PROJECT_NAME="${PROJECT_NAME:-mynicegui}"
GCP_PROJECT_ID="${GCP_PROJECT_ID:-testcopiernicegui}"
GCP_REGION="${GCP_REGION:-europe-west1}"
GAR_REPOSITORY="${GAR_REPOSITORY:-mynicegui}"
IMAGE_VERSION="${IMAGE_VERSION:-latest}"
GAR_URL="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GAR_REPOSITORY}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "${PROJECT_ROOT}/docker"

docker build --target base --tag ${PROJECT_NAME}:base --file Dockerfile ..
docker build --build-arg PROJECT_NAME=${PROJECT_NAME} --tag ${GAR_URL}/${PROJECT_NAME}-backend:${IMAGE_VERSION} --file Dockerfile.backend ..
docker build --build-arg PROJECT_NAME=${PROJECT_NAME} --tag ${GAR_URL}/${PROJECT_NAME}-worker:${IMAGE_VERSION} --file Dockerfile.worker ..
docker build --build-arg PROJECT_NAME=${PROJECT_NAME} --tag ${GAR_URL}/${PROJECT_NAME}-frontend:${IMAGE_VERSION} --file Dockerfile.frontend ..
