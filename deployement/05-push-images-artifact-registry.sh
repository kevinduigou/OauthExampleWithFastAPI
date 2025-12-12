#!/bin/bash
set -e

PROJECT_NAME="${PROJECT_NAME:-mynicegui}"
GCP_PROJECT_ID="${GCP_PROJECT_ID:-testcopiernicegui}"
GCP_REGION="${GCP_REGION:-europe-west1}"
GAR_REPOSITORY="${GAR_REPOSITORY:-mynicegui}"
IMAGE_VERSION="${IMAGE_VERSION:-latest}"
GAR_URL="${GCP_REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GAR_REPOSITORY}"

docker push ${GAR_URL}/${PROJECT_NAME}-backend:${IMAGE_VERSION}
docker push ${GAR_URL}/${PROJECT_NAME}-frontend:${IMAGE_VERSION}
docker push ${GAR_URL}/${PROJECT_NAME}-worker:${IMAGE_VERSION}

