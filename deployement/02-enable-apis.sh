#!/bin/bash
set -e

GCP_PROJECT_ID="${GCP_PROJECT_ID:-testcopiernicegui}"

gcloud services enable \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  redis.googleapis.com \
  vpcaccess.googleapis.com \
  --project=${GCP_PROJECT_ID}

