#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

required_files=(
  ".claude-plugin/marketplace.json"
  ".claude-plugin/plugin.json"
  ".mcp.json"
  ".env.example"
  "codex/INSTALL.md"
  "social/.claude-plugin/plugin.json"
  "social/.mcp.json"
  "social/commands/go-to-market.md"
  "social/commands/post-instagram.md"
  "scripts/run_with_env.sh"
  "scripts/validate_env.sh"
)

required_dirs=(
  "social/skills"
  "skills"
)

for path in "${required_files[@]}"; do
  if [[ ! -f "$path" ]]; then
    echo "[ERROR] Missing required file: $path" >&2
    exit 1
  fi
done

for path in "${required_dirs[@]}"; do
  if [[ ! -d "$path" ]]; then
    echo "[ERROR] Missing required directory: $path" >&2
    exit 1
  fi
done

for gitignore_entry in ".env" ".env.local"; do
  if ! grep -Fqx "${gitignore_entry}" .gitignore; then
    echo "[ERROR] .gitignore must include '${gitignore_entry}'" >&2
    exit 1
  fi
done

required_env_vars=(
  GEMINI_API_KEY
  INSTAGRAM_ACCESS_TOKEN
  INSTAGRAM_USER_ID
  GITHUB_TOKEN
  GITHUB_REPO
  LINKEDIN_CLIENT_ID
  LINKEDIN_CLIENT_SECRET
  LINKEDIN_CLI_REDIRECT_URI
)

for env_var in "${required_env_vars[@]}"; do
  if ! rg -q "^${env_var}=" .env.example; then
    echo "[ERROR] .env.example missing required variable: ${env_var}" >&2
    exit 1
  fi
done

echo "[OK] Environment template and gitignore checks passed"

for json_file in ".claude-plugin/marketplace.json" ".claude-plugin/plugin.json" ".mcp.json" "social/.claude-plugin/plugin.json" "social/.mcp.json"; do
  jq -e . "$json_file" >/dev/null
  echo "[OK] Valid JSON: $json_file"
done

root_version="$(jq -r '.version' .claude-plugin/plugin.json)"
social_version="$(jq -r '.version' social/.claude-plugin/plugin.json)"
market_plugin_version="$(jq -r '.plugins[] | select(.name == "social") | .version' .claude-plugin/marketplace.json)"
market_meta_version="$(jq -r '.metadata.version' .claude-plugin/marketplace.json)"

if [[ "$root_version" != "$social_version" || "$root_version" != "$market_plugin_version" || "$root_version" != "$market_meta_version" ]]; then
  echo "[ERROR] Version mismatch detected:" >&2
  echo "  .claude-plugin/plugin.json: $root_version" >&2
  echo "  social/.claude-plugin/plugin.json: $social_version" >&2
  echo "  .claude-plugin/marketplace.json plugin version: $market_plugin_version" >&2
  echo "  .claude-plugin/marketplace.json metadata.version: $market_meta_version" >&2
  exit 1
fi

echo "[OK] Version consistency: $root_version"

market_source_type="$(jq -r '.plugins[] | select(.name == "social") | .source.source // empty' .claude-plugin/marketplace.json)"
market_source_url="$(jq -r '.plugins[] | select(.name == "social") | .source.url // empty' .claude-plugin/marketplace.json)"

if [[ "$market_source_type" != "url" || -z "$market_source_url" ]]; then
  echo "[ERROR] Marketplace source must be a URL source object for plugin 'social'." >&2
  exit 1
fi

if [[ "$market_source_url" != *.git ]]; then
  echo "[ERROR] Marketplace source URL should end with .git: $market_source_url" >&2
  exit 1
fi

echo "[OK] Marketplace source URL: $market_source_url"

jq -e '.commands == "./social/commands" and .skills == "./skills" and .mcpServers == "./.mcp.json"' .claude-plugin/plugin.json >/dev/null || {
  echo "[ERROR] Root plugin paths must be commands=./social/commands skills=./skills mcpServers=./.mcp.json" >&2
  exit 1
}

jq -e '.commands == "./commands" and .skills == "./skills" and .mcpServers == "./.mcp.json"' social/.claude-plugin/plugin.json >/dev/null || {
  echo "[ERROR] Social plugin paths must be commands=./commands skills=./skills mcpServers=./.mcp.json" >&2
  exit 1
}

echo "[OK] Plugin path fields are correct"

if ! diff -qr social/skills skills >/dev/null; then
  echo "[ERROR] skills/ is not in sync with social/skills. Run ./scripts/sync_social_skills.sh --validate" >&2
  exit 1
fi

echo "[OK] skills/ mirror is in sync"

echo "[OK] Universal packaging validation passed"
