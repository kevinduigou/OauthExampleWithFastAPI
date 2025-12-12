#!/bin/bash
set -e

# Authenticate Docker and set GCP project
GCP_PROJECT_ID="${GCP_PROJECT_ID:-testcopiernicegui}"
GCP_REGION="${GCP_REGION:-europe-west1}"

gcloud auth configure-docker ${GCP_REGION}-docker.pkg.dev --quiet
gcloud config set project ${GCP_PROJECT_ID}

