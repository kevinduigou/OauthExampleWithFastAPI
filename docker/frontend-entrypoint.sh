#!/bin/sh
# Frontend entrypoint script
# Generates config.js with runtime environment variables

# Create config.js with environment variables
cat > /usr/share/nginx/html/config.js << EOF
window.CONFIG = {
  DEPLOYMENT_URL: "${VITE_DEPLOYMENT_URL:-http://localhost:8000}"
};
EOF

echo "Generated config.js with DEPLOYMENT_URL: ${VITE_DEPLOYMENT_URL:-http://localhost:8000}"

# Start nginx
exec nginx -g "daemon off;"
