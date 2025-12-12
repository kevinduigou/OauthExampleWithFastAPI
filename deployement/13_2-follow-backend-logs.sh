#!/bin/bash

# Follow Backend Cloud Run Logs
# This script streams logs from the backend Cloud Run service

set -e

# Configuration with defaults
PROJECT_NAME="${PROJECT_NAME:-mynicegui}"
GCP_PROJECT_ID="${GCP_PROJECT_ID:-testcopiernicegui}"
GCP_REGION="${GCP_REGION:-europe-west1}"
BACKEND_SERVICE_NAME="${BACKEND_SERVICE_NAME:-${PROJECT_NAME}-backend}"

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Following Backend Logs${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}Service:${NC} ${BACKEND_SERVICE_NAME}"
echo -e "${GREEN}Project:${NC} ${GCP_PROJECT_ID}"
echo -e "${GREEN}Region:${NC} ${GCP_REGION}"
echo ""
echo "Press Ctrl+C to stop following logs..."
echo ""

gcloud beta run services logs tail ${BACKEND_SERVICE_NAME} \
    --project=${GCP_PROJECT_ID} \
    --region=${GCP_REGION}
