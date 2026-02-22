#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"
ENV_LOCAL_FILE="$ROOT_DIR/.env.local"

profile="all"
load_files=0

usage() {
  cat <<'USAGE'
Usage: ./scripts/validate_env.sh [--profile <all|media|instagram|linkedin>] [--load]

Validates required environment variables for selected workflows.

Options:
  --profile   Validation profile. Default: all
  --load      Load .env and .env.local before validation

Profiles:
  media       GEMINI_API_KEY
  instagram   INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_USER_ID, GITHUB_TOKEN, GITHUB_REPO
  linkedin    LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, LINKEDIN_CLI_REDIRECT_URI
  all         Union of all profiles
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile)
      profile="${2:-}"
      shift 2
      ;;
    --load)
      load_files=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[ERROR] Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

case "$profile" in
  all|media|instagram|linkedin)
    ;;
  *)
    echo "[ERROR] Invalid profile: $profile" >&2
    usage
    exit 1
    ;;
esac

if [[ "$load_files" -eq 1 ]]; then
  if [[ -f "$ENV_FILE" ]]; then
    # shellcheck source=/dev/null
    set -a
    source "$ENV_FILE"
    set +a
  fi
  if [[ -f "$ENV_LOCAL_FILE" ]]; then
    # shellcheck source=/dev/null
    set -a
    source "$ENV_LOCAL_FILE"
    set +a
  fi
fi

required_vars=()
case "$profile" in
  media)
    required_vars=(
      GEMINI_API_KEY
    )
    ;;
  instagram)
    required_vars=(
      INSTAGRAM_ACCESS_TOKEN
      INSTAGRAM_USER_ID
      GITHUB_TOKEN
      GITHUB_REPO
    )
    ;;
  linkedin)
    required_vars=(
      LINKEDIN_CLIENT_ID
      LINKEDIN_CLIENT_SECRET
      LINKEDIN_CLI_REDIRECT_URI
    )
    ;;
  all)
    required_vars=(
      GEMINI_API_KEY
      INSTAGRAM_ACCESS_TOKEN
      INSTAGRAM_USER_ID
      GITHUB_TOKEN
      GITHUB_REPO
      LINKEDIN_CLIENT_ID
      LINKEDIN_CLIENT_SECRET
      LINKEDIN_CLI_REDIRECT_URI
    )
    ;;
esac

missing=()

echo "[INFO] Validating profile: $profile"
for var_name in "${required_vars[@]}"; do
  var_value="${!var_name:-}"
  if [[ -z "$var_value" ]]; then
    missing+=("$var_name")
    echo "[MISSING] $var_name"
  else
    echo "[OK] $var_name"
  fi
done

if [[ ${#missing[@]} -gt 0 ]]; then
  echo "[ERROR] Missing ${#missing[@]} required variable(s)." >&2
  if [[ "$load_files" -eq 0 ]]; then
    echo "[INFO] Tip: run with --load to validate values from .env/.env.local" >&2
  fi
  exit 1
fi

echo "[OK] Environment validation passed"
