#!/bin/bash
set -e

GCP_PROJECT_ID="${GCP_PROJECT_ID:-testcopiernicegui}"
VOLUME_NAME="${VOLUME_NAME:-mynicegui-data}"
GCP_REGION="${GCP_REGION:-europe-west1}"
BUCKET_NAME="${GCP_PROJECT_ID}-${VOLUME_NAME}"

if ! gcloud storage buckets describe gs://${BUCKET_NAME} --project=${GCP_PROJECT_ID} &>/dev/null; then
  gcloud storage buckets create gs://${BUCKET_NAME} --location=${GCP_REGION} --project=${GCP_PROJECT_ID}
fi

