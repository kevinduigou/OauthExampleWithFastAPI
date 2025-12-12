#!/bin/bash
set -e

GCP_PROJECT_ID="${GCP_PROJECT_ID:-testcopiernicegui}"
GCP_REGION="${GCP_REGION:-europe-west1}"
GAR_REPOSITORY="${GAR_REPOSITORY:-mynicegui}"

if ! gcloud artifacts repositories describe ${GAR_REPOSITORY} --location=${GCP_REGION} --project=${GCP_PROJECT_ID} &>/dev/null; then
  gcloud artifacts repositories create ${GAR_REPOSITORY} \
    --repository-format=docker \
    --location=${GCP_REGION} \
    --description="Docker repository for ${GAR_REPOSITORY}" \
    --project=${GCP_PROJECT_ID}
fi

