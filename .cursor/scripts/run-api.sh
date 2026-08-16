#!/usr/bin/env bash
# Long-running API dev server (NestJS + nodemon) on http://localhost:8080/api
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "$SCRIPT_DIR/lib.sh"

use_node_20
cd "$REPO_ROOT/packages/api"
exec yarn start:dev
