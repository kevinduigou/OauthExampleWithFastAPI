#!/bin/bash

# Deploy RQ Worker to Google Cloud VM Script
# This script creates a VM, installs uv and Python, copies project files,
# and runs the RQ worker directly (no Docker)

set -e  # Exit on error

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration with defaults
PROJECT_NAME="${PROJECT_NAME:-mynicegui}"
GCP_PROJECT_ID="${GCP_PROJECT_ID:-testcopiernicegui}"
GCP_REGION="${GCP_REGION:-europe-west1}"
GCP_ZONE="${GCP_ZONE:-europe-west1-b}"
VM_NAME="${VM_NAME:-${PROJECT_NAME}-worker-vm}"
MACHINE_TYPE="${MACHINE_TYPE:-e2-medium}"
PYTHON_VERSION="${PYTHON_VERSION:-3.12}"

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo_step() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

echo_step "Deploy RQ Worker to Google Cloud VM"
echo ""
echo "Configuration:"
echo "  Project ID: ${GCP_PROJECT_ID}"
echo "  Region: ${GCP_REGION}"
echo "  Zone: ${GCP_ZONE}"
echo "  VM Name: ${VM_NAME}"
echo "  Machine Type: ${MACHINE_TYPE}"
echo "  Python Version: ${PYTHON_VERSION}"
echo ""

# Check if .env file exists
ENV_FILE=""
if [ -f "${SCRIPT_DIR}/.env" ]; then
    ENV_FILE="${SCRIPT_DIR}/.env"
elif [ -f "${SCRIPT_DIR}/.env-prod" ]; then
    ENV_FILE="${SCRIPT_DIR}/.env-prod"
elif [ -f "${PROJECT_ROOT}/.env" ]; then
    ENV_FILE="${PROJECT_ROOT}/.env"
    echo_warn "Using .env file from project root"
else
    echo_error "Error: .env file not found"
    echo "Please create one of the following:"
    echo "  - ${SCRIPT_DIR}/.env"
    echo "  - ${SCRIPT_DIR}/.env-prod"
    echo "  - ${PROJECT_ROOT}/.env"
    exit 1
fi

echo_info "Using environment file: ${ENV_FILE}"
echo ""


# Step 3: Create or use existing VM instance
echo_step "Step 3: Checking VM instance"

# Check if VM already exists
if gcloud compute instances describe ${VM_NAME} \
    --zone=${GCP_ZONE} \
    --project=${GCP_PROJECT_ID} &>/dev/null; then

    echo_info "VM '${VM_NAME}' already exists. Skipping creation and proceeding to deployment..."
else
    echo_info "Creating new VM instance..."
    gcloud compute instances create "${VM_NAME}" \
        --zone="${GCP_ZONE}" \
        --machine-type="${MACHINE_TYPE}" \
        --image-family="debian-12" \
        --image-project="debian-cloud" \
        --boot-disk-size="20GB" \
        --boot-disk-type="pd-standard" \
        --scopes="cloud-platform" \
        --metadata="google-logging-enabled=true" \
        --project="${GCP_PROJECT_ID}"

    echo_info "VM instance created successfully"

    # Step 4: Wait for SSH to be ready (only for new VMs)
    echo_step "Step 4: Waiting for SSH to be ready"

    max_attempts=30
    attempt=1

    while [ $attempt -le $max_attempts ]; do
        echo_info "Attempt $attempt/$max_attempts: Testing SSH connection..."

        if gcloud compute ssh ${VM_NAME} \
            --zone=${GCP_ZONE} \
            --project=${GCP_PROJECT_ID} \
            --command="echo 'SSH ready'" \
            --ssh-flag="-o ConnectTimeout=10" \
            --ssh-flag="-o StrictHostKeyChecking=no" \
            --ssh-flag="-o UserKnownHostsFile=/dev/null" \
            &> /dev/null; then
            echo_info "SSH is ready!"
            break
        fi
        
        if [ $attempt -lt $max_attempts ]; then
            echo_info "SSH not ready yet, waiting 10 seconds..."
            sleep 10
        else
            echo_error "SSH did not become ready within timeout"
            exit 1
        fi
        ((attempt++))
    done
fi

# Step 5: Install dependencies on VM
echo_step "Step 5: Installing dependencies on VM"

INSTALL_SCRIPT=$(cat << 'EOFINSTALL'
#!/bin/bash
set -e

echo "Updating system packages..."
sudo apt-get update
sudo apt-get install -y curl build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget llvm \
    libncurses5-dev libncursesw5-dev xz-utils tk-dev \
    libffi-dev liblzma-dev git

echo "Installing uv..."
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH for current session
export PATH="$HOME/.local/bin:$PATH"

echo "uv installed successfully"
uv --version
EOFINSTALL
)

echo_info "Executing installation script on VM..."
gcloud compute ssh ${VM_NAME} \
    --zone=${GCP_ZONE} \
    --project=${GCP_PROJECT_ID} \
    --command="${INSTALL_SCRIPT}"

# Step 6: Create project directory and copy files
echo_step "Step 6: Copying project files to VM"

# Create project directory on VM
gcloud compute ssh ${VM_NAME} \
    --zone=${GCP_ZONE} \
    --project=${GCP_PROJECT_ID} \
    --command="mkdir -p ~/${PROJECT_NAME}"

# Create temporary directory for files to copy
TEMP_DIR=$(mktemp -d)

# Copy essential project files
cp "${PROJECT_ROOT}/pyproject.toml" "${TEMP_DIR}/"
cp "${PROJECT_ROOT}/uv.lock" "${TEMP_DIR}/"
cp "${PROJECT_ROOT}/README.md" "${TEMP_DIR}/"

# Copy backend source code (excluding __pycache__ and .pyc files)
rsync -av --exclude='__pycache__' --exclude='*.pyc' "${PROJECT_ROOT}/backend/" "${TEMP_DIR}/backend/"

echo_info "Copying production environment file..."
cp "${PROJECT_ROOT}/.env-prod" "${TEMP_DIR}/.env"

echo_info "Copying files to VM..."
gcloud compute scp --recurse "${TEMP_DIR}/"* ${VM_NAME}:~/${PROJECT_NAME}/ \
    --zone=${GCP_ZONE} \
    --project=${GCP_PROJECT_ID} \
    --scp-flag="-o StrictHostKeyChecking=no" \
    --scp-flag="-o UserKnownHostsFile=/dev/null"

echo_info "Copying .env file to VM..."
gcloud compute scp "${TEMP_DIR}/.env" ${VM_NAME}:~/${PROJECT_NAME}/.env \
    --zone=${GCP_ZONE} \
    --project=${GCP_PROJECT_ID} \
    --scp-flag="-o StrictHostKeyChecking=no" \
    --scp-flag="-o UserKnownHostsFile=/dev/null"

# Clean up temp directory
rm -rf "${TEMP_DIR}"

echo_info "Files copied successfully"

# Step 7: Set up Python environment and install dependencies
echo_step "Step 7: Setting up Python environment"

SETUP_ENV_SCRIPT=$(cat << EOFSETUP
#!/bin/bash
set -e

# Add uv to PATH
export PATH="\$HOME/.local/bin:\$PATH"

cd ~/${PROJECT_NAME}

echo "Creating Python virtual environment with uv..."
uv venv --python ${PYTHON_VERSION}

echo "Installing project dependencies..."
uv sync --no-dev

echo "Python environment setup complete"
EOFSETUP
)

echo_info "Setting up Python environment on VM..."
gcloud compute ssh ${VM_NAME} \
    --zone=${GCP_ZONE} \
    --project=${GCP_PROJECT_ID} \
    --command="${SETUP_ENV_SCRIPT}"

# Step 8: Create systemd service for RQ worker
echo_step "Step 8: Creating systemd service for RQ worker"

# Get current user on VM
VM_USER=$(gcloud compute ssh ${VM_NAME} \
    --zone=${GCP_ZONE} \
    --project=${GCP_PROJECT_ID} \
    --command="whoami")

SERVICE_FILE=$(cat << EOFSERVICE
[Unit]
Description=RQ Worker for ${PROJECT_NAME}
After=network.target

[Service]
Type=simple
User=${VM_USER}
WorkingDirectory=/home/${VM_USER}/${PROJECT_NAME}
EnvironmentFile=/home/${VM_USER}/${PROJECT_NAME}/.env
ExecStart=/home/${VM_USER}/${PROJECT_NAME}/.venv/bin/rq worker --with-scheduler default
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=rq-worker

[Install]
WantedBy=multi-user.target
EOFSERVICE
)

# Create service file on VM
gcloud compute ssh ${VM_NAME} \
    --zone=${GCP_ZONE} \
    --project=${GCP_PROJECT_ID} \
    --command="echo '${SERVICE_FILE}' | sudo tee /etc/systemd/system/rq-worker.service > /dev/null"

# Enable and start the service
START_SERVICE_SCRIPT=$(cat << 'EOFSTART'
#!/bin/bash
set -e

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling RQ worker service..."
sudo systemctl enable rq-worker.service

echo "Starting RQ worker service..."
sudo systemctl start rq-worker.service

echo "Checking service status..."
sudo systemctl status rq-worker.service --no-pager
EOFSTART
)

echo_info "Starting RQ worker service..."
gcloud compute ssh ${VM_NAME} \
    --zone=${GCP_ZONE} \
    --project=${GCP_PROJECT_ID} \
    --command="${START_SERVICE_SCRIPT}"

# Step 9: Display deployment information
echo ""
echo_step "Deployment Complete!"
echo ""
echo_info "VM Name: ${VM_NAME}"
echo_info "Zone: ${GCP_ZONE}"
echo_info "Project: ${GCP_PROJECT_ID}"
echo ""
echo_info "RQ Worker is running as a systemd service"
echo ""
echo "Useful commands:"
echo ""
echo "SSH to VM:"
echo "  gcloud compute ssh ${VM_NAME} --zone=${GCP_ZONE} --project=${GCP_PROJECT_ID}"
echo ""
echo "View worker logs:"
echo "  gcloud compute ssh ${VM_NAME} --zone=${GCP_ZONE} --project=${GCP_PROJECT_ID} --command='sudo journalctl -u rq-worker -f'"
echo ""
echo "Check worker status:"
echo "  gcloud compute ssh ${VM_NAME} --zone=${GCP_ZONE} --project=${GCP_PROJECT_ID} --command='sudo systemctl status rq-worker'"
echo ""
echo "Restart worker:"
echo "  gcloud compute ssh ${VM_NAME} --zone=${GCP_ZONE} --project=${GCP_PROJECT_ID} --command='sudo systemctl restart rq-worker'"
echo ""
echo "Stop worker:"
echo "  gcloud compute ssh ${VM_NAME} --zone=${GCP_ZONE} --project=${GCP_PROJECT_ID} --command='sudo systemctl stop rq-worker'"
echo ""
echo "Update code and restart:"
echo "  ./update-worker-vm.sh"
echo ""
echo "Delete VM:"
echo "  gcloud compute instances delete ${VM_NAME} --zone=${GCP_ZONE} --project=${GCP_PROJECT_ID}"
echo ""
