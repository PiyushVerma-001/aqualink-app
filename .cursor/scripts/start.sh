#!/usr/bin/env bash
# Per-boot runtime initialization: bring up PostgreSQL/PostGIS, ensure the
# development and test databases exist, and apply API migrations. Idempotent.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "$SCRIPT_DIR/lib.sh"

PG_VER="$(pg_version)"
if [ -z "$PG_VER" ]; then
  echo "ERROR: no PostgreSQL installation found under /etc/postgresql" >&2
  exit 1
fi

echo "==> Ensuring PostgreSQL $PG_VER cluster 'main' is running"
if ! pg_lsclusters -h 2>/dev/null | awk -v v="$PG_VER" '$1==v && $2=="main"{print $4}' | grep -q online; then
  sudo pg_ctlcluster "$PG_VER" main start
fi

echo "==> Waiting for PostgreSQL to accept connections"
for _ in $(seq 1 30); do
  if pg_isready -h 127.0.0.1 -p 5432 >/dev/null 2>&1; then break; fi
  sleep 1
done
pg_isready -h 127.0.0.1 -p 5432 >/dev/null 2>&1 || { echo "ERROR: PostgreSQL did not become ready" >&2; exit 1; }

echo "==> Ensuring 'postgres' role password and databases exist"
sudo -u postgres psql -v ON_ERROR_STOP=1 -qc "ALTER USER postgres PASSWORD 'postgres';"
sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='test_aqualink'" | grep -q 1 \
  || sudo -u postgres psql -v ON_ERROR_STOP=1 -qc "CREATE DATABASE test_aqualink;"

echo "==> Applying API migrations on the development database"
use_node_20
cd "$REPO_ROOT/packages/api"
DATABASE_URL="postgres://postgres:postgres@localhost:5432/postgres" \
BACKEND_BASE_URL="http://localhost:8080/api" \
TZ=UTC \
  yarn migration:run

echo "==> start.sh complete; PostgreSQL is ready on localhost:5432"
