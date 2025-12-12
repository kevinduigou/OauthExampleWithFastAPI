#!/bin/bash
set -e

GCP_PROJECT_ID="${GCP_PROJECT_ID:-testcopiernicegui}"
GCP_REGION="${GCP_REGION:-europe-west1}"
SERVICE_NAME="${SERVICE_NAME:-mynicegui-app}"
VPC_CONNECTOR_NAME="${SERVICE_NAME}-connector"

if ! gcloud compute networks vpc-access connectors describe ${VPC_CONNECTOR_NAME} --region=${GCP_REGION} --project=${GCP_PROJECT_ID} &>/dev/null; then
  gcloud compute networks vpc-access connectors create ${VPC_CONNECTOR_NAME} \
    --region=${GCP_REGION} \
    --network=default \
    --range=10.8.0.0/28 \
    --project=${GCP_PROJECT_ID}
fi

