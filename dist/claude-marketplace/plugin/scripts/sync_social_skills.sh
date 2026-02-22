#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$ROOT_DIR/social/skills"
TARGET_DIR="$ROOT_DIR/skills"
VALIDATE=0

usage() {
  cat <<'USAGE'
Usage: ./scripts/sync_social_skills.sh [--validate]

Mirrors social plugin skills into the repository-level skills directory.

Options:
  --validate   Validate mirrored skills after sync.
USAGE
}

for arg in "$@"; do
  case "$arg" in
    --validate)
      VALIDATE=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "[ERROR] Unknown argument: $arg" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "[ERROR] Source skills directory not found: $SOURCE_DIR" >&2
  exit 1
fi

rm -rf "$TARGET_DIR"
mkdir -p "$TARGET_DIR"

rsync -a --delete --exclude '__pycache__/' --exclude '.DS_Store' "$SOURCE_DIR/" "$TARGET_DIR/"
find "$TARGET_DIR" -type d -name '__pycache__' -prune -exec rm -rf {} +

echo "[OK] Mirrored skills: $SOURCE_DIR -> $TARGET_DIR"

if [[ "$VALIDATE" -eq 1 ]]; then
  failures=0
  names_file="$(mktemp)"

  for skill_dir in "$TARGET_DIR"/*; do
    [[ -d "$skill_dir" ]] || continue
    skill_file="$skill_dir/SKILL.md"
    dir_name="$(basename "$skill_dir")"

    if [[ ! -f "$skill_file" ]]; then
      echo "[ERROR] Missing SKILL.md: $skill_dir" >&2
      failures=$((failures + 1))
      continue
    fi

    if [[ "$(head -n 1 "$skill_file")" != "---" ]]; then
      echo "[ERROR] Missing frontmatter delimiter in: $skill_file" >&2
      failures=$((failures + 1))
      continue
    fi

    skill_name="$(sed -n 's/^name:[[:space:]]*//p' "$skill_file" | head -n 1 | tr -d '\"' | tr -d "'" | xargs)"
    if [[ -z "$skill_name" ]]; then
      echo "[ERROR] Missing 'name' field in frontmatter: $skill_file" >&2
      failures=$((failures + 1))
      continue
    fi

    if [[ "$skill_name" != "$dir_name" ]]; then
      echo "[ERROR] Skill name and directory mismatch: name='$skill_name' dir='$dir_name' ($skill_file)" >&2
      failures=$((failures + 1))
    fi

    echo "$skill_name" >> "$names_file"
  done

  duplicate_names="$(sort "$names_file" | uniq -d || true)"
  rm -f "$names_file"

  if [[ -n "$duplicate_names" ]]; then
    while IFS= read -r dup; do
      [[ -n "$dup" ]] || continue
      echo "[ERROR] Duplicate skill name: $dup" >&2
      failures=$((failures + 1))
    done <<< "$duplicate_names"
  fi

  if [[ "$failures" -gt 0 ]]; then
    echo "[ERROR] Validation failed with $failures issue(s)." >&2
    exit 1
  fi

  echo "[OK] Skill validation passed"
fi
