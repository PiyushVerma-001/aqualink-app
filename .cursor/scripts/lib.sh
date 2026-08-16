#!/usr/bin/env bash
# Shared helpers for Aqualink Cloud Agent environment scripts.

# Resolve the repository root regardless of where a script is invoked from.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export REPO_ROOT

# The repo requires Node 20 (see package.json "engines"). The base image ships a
# newer Node on PATH, so select Node 20 via nvm and put it first on PATH.
use_node_20() {
  export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
  # shellcheck disable=SC1091
  [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
  if command -v nvm >/dev/null 2>&1; then
    nvm install 20 >/dev/null 2>&1 || true
    local node20
    node20="$(nvm which 20 2>/dev/null || true)"
    if [ -n "$node20" ]; then
      export PATH="$(dirname "$node20"):$PATH"
    fi
  fi
  # nvm's Node 20 does not ship yarn, and the base shell does not reliably
  # expose a yarn on PATH once Node 20 is prepended, so ensure the classic
  # yarn the repo uses (see package.json "packageManager") is installed.
  if ! command -v yarn >/dev/null 2>&1; then
    npm install -g yarn@1.22.22 >/dev/null 2>&1 || true
  fi
  echo "Using node $(node -v) / yarn $(yarn -v)"
}

# Detect the installed PostgreSQL major version (e.g. "16").
pg_version() {
  ls /etc/postgresql 2>/dev/null | sort -V | tail -1
}
