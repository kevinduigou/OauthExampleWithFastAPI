#!/bin/bash
set -e

GCP_PROJECT_ID="${GCP_PROJECT_ID:-testcopiernicegui}"
GCP_REGION="${GCP_REGION:-europe-west1}"
SERVICE_NAME="${SERVICE_NAME:-mynicegui-app}"
REDIS_INSTANCE_NAME="${SERVICE_NAME}-redis"

if ! gcloud redis instances describe ${REDIS_INSTANCE_NAME} --region=${GCP_REGION} --project=${GCP_PROJECT_ID} &>/dev/null; then
  gcloud redis instances create ${REDIS_INSTANCE_NAME} \
    --size=1 \
    --region=${GCP_REGION} \
    --redis-version=redis_7_0 \
    --tier=basic \
    --project=${GCP_PROJECT_ID}
fi

REDIS_HOST=$(gcloud redis instances describe ${REDIS_INSTANCE_NAME} --region=${GCP_REGION} --project=${GCP_PROJECT_ID} --format="value(host)")
REDIS_PORT=$(gcloud redis instances describe ${REDIS_INSTANCE_NAME} --region=${GCP_REGION} --project=${GCP_PROJECT_ID} --format="value(port)")
echo "REDIS_URL=redis://${REDIS_HOST}:${REDIS_PORT}/0"

