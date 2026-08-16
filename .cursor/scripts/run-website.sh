#!/usr/bin/env bash
# Long-running website dev server (rsbuild) on http://localhost:3000
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
. "$SCRIPT_DIR/lib.sh"

use_node_20
cd "$REPO_ROOT/packages/website"
exec yarn start
