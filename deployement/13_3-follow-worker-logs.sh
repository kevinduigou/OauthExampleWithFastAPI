#!/bin/bash

# Follow RQ Worker Logs on VM
# This script streams logs from the RQ worker systemd service on the VM

set -e

# Configuration with defaults
PROJECT_NAME="${PROJECT_NAME:-mynicegui}"
GCP_PROJECT_ID="${GCP_PROJECT_ID:-testcopiernicegui}"
GCP_ZONE="${GCP_ZONE:-europe-west1-b}"
VM_NAME="${VM_NAME:-${PROJECT_NAME}-worker-vm}"

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Following RQ Worker Logs${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}VM:${NC} ${VM_NAME}"
echo -e "${GREEN}Project:${NC} ${GCP_PROJECT_ID}"
echo -e "${GREEN}Zone:${NC} ${GCP_ZONE}"
echo ""
echo "Press Ctrl+C to stop following logs..."
echo ""

gcloud compute ssh ${VM_NAME} \
    --zone=${GCP_ZONE} \
    --project=${GCP_PROJECT_ID} \
    --command='sudo journalctl -u rq-worker -f'
