#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${1:-${PROJECT_ROOT}/.env-prod}"  # Pass as argument or fallback

REDIS_URL="${REDIS_URL:-}"
BASE_URL="${BASE_URL:-}"

ENV_VARS_FILE="${PROJECT_ROOT}/env-vars.yaml"
echo "REDIS_URL: \"${REDIS_URL}\"" > "$ENV_VARS_FILE"


# Read each line from the environment file
while IFS= read -r line || [ -n "$line" ]; do
  # Skip lines that are comments or empty
  if [[ ! "$line" =~ ^[[:space:]]*# ]] && [[ -n "$line" ]]; then
    # Remove any inline comment (anything after '#')
    line=$(echo "$line" | sed "s/#.*$//")
    # Trim leading and trailing whitespace
    line=$(echo "$line" | xargs)
    # Only process non-empty lines that contain an '=' sign
    if [[ -n "$line" ]] && [[ "$line" == *"="* ]]; then
      # Extract the key (part before the first '=')
      key="${line%%=*}"
      # Extract the value (part after the first '=')
      value="${line#*=}"
      # Skip keys named 'REDIS_URL' or 'BASE_URL'
      if [[ "$key" != "REDIS_URL" && "$key" != "BASE_URL" ]]; then
        # Output the key-value pair in YAML format to the env vars file
        echo "${key}: \"${value}\"" >> "$ENV_VARS_FILE"
      fi
    fi
  fi
done < "${ENV_FILE}"


echo "BASE_URL: \"${BASE_URL}\"" >> "$ENV_VARS_FILE"
echo "Environment variables written to: $ENV_VARS_FILE"
