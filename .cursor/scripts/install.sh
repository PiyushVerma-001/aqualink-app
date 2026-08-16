#!/usr/bin/env bash
# Idempotent dependency + local-config bootstrap for the Aqualink monorepo.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "$SCRIPT_DIR/lib.sh"

use_node_20
cd "$REPO_ROOT"

echo "==> Installing workspace dependencies (yarn install)"
yarn install --frozen-lockfile

# Create local .env files for development if they do not already exist.
# These point the API and website at the local PostgreSQL/PostGIS instance
# started by start.sh. They are gitignored.
API_ENV="$REPO_ROOT/packages/api/.env.local"
if [ ! -f "$API_ENV" ]; then
  echo "==> Writing packages/api/.env.local"
  cat > "$API_ENV" <<'EOF'
NODE_ENV=development
DATABASE_URL=postgres://postgres:postgres@localhost:5432/postgres
TEST_DATABASE_URL=postgres://postgres:postgres@localhost:5432/test_aqualink
BACKEND_BASE_URL=http://localhost:8080/api
PORT=8080
TZ=UTC
STORAGE_MAX_FILE_SIZE_MB=1
EOF
fi

WEBSITE_ENV="$REPO_ROOT/packages/website/.env"
if [ ! -f "$WEBSITE_ENV" ]; then
  echo "==> Writing packages/website/.env"
  cat > "$WEBSITE_ENV" <<'EOF'
REACT_APP_API_BASE_URL=http://localhost:8080/api
REACT_APP_FEATURED_SITE_ID=1
EOF
fi

echo "==> install.sh complete"
