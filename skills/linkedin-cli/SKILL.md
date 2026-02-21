---
name: linkedin-cli
description: Create or refactor a generic CLI for LinkedIn integrations. Use when users need LinkedIn OAuth, posting, post retrieval/history, analytics, output contracts, or safe automation with dry-run/confirmation behavior.
---

# LinkedIn CLI Skill

Builds a self-contained, reusable LinkedIn command interface that works in any project.

## When To Use

Use this skill when the user asks to:
- create or redesign a LinkedIn CLI
- implement LinkedIn OAuth login/token exchange in a CLI
- publish LinkedIn posts from terminal workflows
- return complete metadata for created posts
- fetch LinkedIn post details, history, or engagement stats
- enforce safe side-effect behavior (`--dry-run`, confirmation, non-interactive rules)

## Required Files In This Skill

Read these before editing target-project code:
- `references/cli_spec.md`
- `references/output_contracts.md`

Use these bundled resources directly when useful:
- `scripts/linkedin_cli.py` (drop-in baseline implementation)
- `assets/contracts/post_receipt.schema.json`
- `assets/contracts/post_analytics.schema.json`

## Workflow

1. Confirm scope
- LinkedIn-only CLI surface.
- No project-specific naming, paths, or business logic.
- Preserve existing ecosystem constraints in target repo (language, linting, release flow).

2. Apply command surface
- Implement command groups from `references/cli_spec.md`.
- Preserve config/env precedence and exit-code contracts.
- Keep output modes stable: human, `--json`, `--plain`.

3. Implement auth and posting safely
- OAuth URL generation + code exchange.
- Secure token handling using file/stdin import (never plaintext token flags).
- Require confirmation for side effects unless `--force` or `--dry-run`.

4. Implement post observability
- On every publish, emit a post receipt object.
- Persist event ledger (`jsonl`) for replay and auditing.
- Provide commands to fetch remote post details and local history.

5. Implement analytics retrieval
- Fetch engagement details for a post URN.
- Normalize response into the analytics contract.

6. Validate
- Check `--help` for top-level and nested subcommands.
- Run at least one dry-run publish flow.
- Validate payload shapes against bundled JSON schemas.

## Non-Negotiable Rules

- Keep the skill generic. Do not embed company/product/project context.
- Use deterministic CLI behavior and stable error codes.
- Keep secrets out of command-line history.
- Prefer idempotent local state operations.
- Side-effect commands must be safe by default.

## Output Requirements

Whenever this skill is applied, ensure created-post output includes:
- LinkedIn post URN (`post_urn`) when available
- derived canonical post URL (`post_url`) when derivable
- author URN
- visibility and lifecycle state
- request timestamp and request-id/header trace values
- raw API response payload (or explicit unavailability)
- local ledger event metadata (path and event id)
