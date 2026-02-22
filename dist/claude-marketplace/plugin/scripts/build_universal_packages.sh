#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
VERSION="$(jq -r '.version' "$ROOT_DIR/.claude-plugin/plugin.json")"

"$ROOT_DIR/scripts/sync_social_skills.sh" --validate
"$ROOT_DIR/scripts/validate_universal_packages.sh"

rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

CLAUDE_STAGE="$DIST_DIR/claude-marketplace"
PLUGIN_STAGE="$CLAUDE_STAGE/plugin"

mkdir -p "$CLAUDE_STAGE/.claude-plugin" "$PLUGIN_STAGE/.claude-plugin" "$PLUGIN_STAGE/codex" "$PLUGIN_STAGE/scripts"

jq '.plugins = (.plugins | map(if .name == "social" then .source = "./plugin" else . end))' \
  "$ROOT_DIR/.claude-plugin/marketplace.json" > "$CLAUDE_STAGE/.claude-plugin/marketplace.json"

cp "$ROOT_DIR/.claude-plugin/plugin.json" "$PLUGIN_STAGE/.claude-plugin/plugin.json"
cp "$ROOT_DIR/.mcp.json" "$PLUGIN_STAGE/.mcp.json"
cp "$ROOT_DIR/.env.example" "$PLUGIN_STAGE/.env.example"
cp "$ROOT_DIR/LICENSE" "$PLUGIN_STAGE/LICENSE"
cp "$ROOT_DIR/README.md" "$PLUGIN_STAGE/README.md"
cp "$ROOT_DIR/codex/INSTALL.md" "$PLUGIN_STAGE/codex/INSTALL.md"
rsync -a --exclude '__pycache__/' --exclude '.DS_Store' "$ROOT_DIR/scripts/" "$PLUGIN_STAGE/scripts/"

rsync -a --exclude '__pycache__/' --exclude '.DS_Store' "$ROOT_DIR/social/" "$PLUGIN_STAGE/social/"
rsync -a --exclude '__pycache__/' --exclude '.DS_Store' "$ROOT_DIR/skills/" "$PLUGIN_STAGE/skills/"

tar -czf "$DIST_DIR/topnotch-social-claude-marketplace-v${VERSION}.tar.gz" -C "$CLAUDE_STAGE" .
cp "$DIST_DIR/topnotch-social-claude-marketplace-v${VERSION}.tar.gz" "$DIST_DIR/topnotch-social-claude-marketplace.tar.gz"

echo "[OK] Built Claude bundle: $DIST_DIR/topnotch-social-claude-marketplace-v${VERSION}.tar.gz"

CODEX_STAGE="$DIST_DIR/codex-skills"
mkdir -p "$CODEX_STAGE/codex" "$CODEX_STAGE/skills" "$CODEX_STAGE/scripts"

cp "$ROOT_DIR/codex/INSTALL.md" "$CODEX_STAGE/codex/INSTALL.md"
cp "$ROOT_DIR/README.md" "$CODEX_STAGE/README.md"
cp "$ROOT_DIR/.env.example" "$CODEX_STAGE/.env.example"
cp "$ROOT_DIR/LICENSE" "$CODEX_STAGE/LICENSE"
rsync -a --exclude '__pycache__/' --exclude '.DS_Store' "$ROOT_DIR/scripts/" "$CODEX_STAGE/scripts/"

rsync -a --exclude '__pycache__/' --exclude '.DS_Store' "$ROOT_DIR/skills/" "$CODEX_STAGE/skills/"

tar -czf "$DIST_DIR/topnotch-social-codex-skills-v${VERSION}.tar.gz" -C "$CODEX_STAGE" .
cp "$DIST_DIR/topnotch-social-codex-skills-v${VERSION}.tar.gz" "$DIST_DIR/topnotch-social-codex-skills.tar.gz"
cp "$DIST_DIR/topnotch-social-codex-skills-v${VERSION}.tar.gz" "$DIST_DIR/topnotch-social-agent-skills.tar.gz"

echo "[OK] Built Codex skills bundle: $DIST_DIR/topnotch-social-codex-skills-v${VERSION}.tar.gz"
echo "[OK] Dist artifacts available in: $DIST_DIR"
