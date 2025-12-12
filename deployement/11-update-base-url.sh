#!/bin/bash
set -e

GCP_PROJECT_ID="${GCP_PROJECT_ID:-testcopiernicegui}"
GCP_REGION="${GCP_REGION:-europe-west1}"
SERVICE_NAME="${SERVICE_NAME:-mynicegui-app}"

SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${GCP_REGION} --project=${GCP_PROJECT_ID} --format="value(status.url)")
ENV_VARS_FILE=$(mktemp)
echo "BASE_URL: \"${SERVICE_URL}\"" >> "$ENV_VARS_FILE"

gcloud run services update ${SERVICE_NAME} \
  --region=${GCP_REGION} \
  --project=${GCP_PROJECT_ID} \
  --env-vars-file="${ENV_VARS_FILE}"

rm -f "$ENV_VARS_FILE"

