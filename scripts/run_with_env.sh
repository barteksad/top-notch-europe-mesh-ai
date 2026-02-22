#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"
ENV_LOCAL_FILE="$ROOT_DIR/.env.local"

usage() {
  cat <<'USAGE'
Usage: ./scripts/run_with_env.sh <command> [args...]

Loads env variables from .env and .env.local (if present), then execs the command.

Examples:
  ./scripts/run_with_env.sh claude
  ./scripts/run_with_env.sh codex
  ./scripts/run_with_env.sh python3 social/scripts/generate_image.py --help
USAGE
}

if [[ $# -lt 1 ]]; then
  usage
  exit 1
fi

loaded_files=()

load_env_file() {
  local file_path="$1"
  if [[ -f "$file_path" ]]; then
    # shellcheck source=/dev/null
    set -a
    source "$file_path"
    set +a
    loaded_files+=("$file_path")
  fi
}

load_env_file "$ENV_FILE"
load_env_file "$ENV_LOCAL_FILE"

if [[ ${#loaded_files[@]} -eq 0 ]]; then
  echo "[WARN] No .env or .env.local file found in $ROOT_DIR" >&2
  echo "[WARN] Continuing with current shell environment only." >&2
else
  echo "[OK] Loaded env files:" >&2
  for file_path in "${loaded_files[@]}"; do
    echo "  - $file_path" >&2
  done
fi

exec "$@"
