# LinkedIn CLI Specification (Generic)

## Name

`linkedin-cli`

## One-Liner

Reusable command interface for LinkedIn authentication, publishing, post retrieval, and analytics.

## Usage

`linkedin-cli [global flags] <command> [subcommand] [args]`

## Command Tree

- `linkedin-cli init`
- `linkedin-cli auth connect|import-token|login|exchange-code|whoami|status|revoke`
- `linkedin-cli post create|get|list|history`
- `linkedin-cli analytics get`
- `linkedin-cli completion`

## Global Flags

| Flag | Type | Default | Notes |
|---|---|---:|---|
| `-h`, `--help` | bool | `false` | Show help and exit. |
| `--version` | bool | `false` | Print version and exit. |
| `--config <path>` | string | project default | Project config override. |
| `--profile <name>` | string | `default` | Profile namespace for auth state. |
| `-q`, `--quiet` | bool | `false` | Minimize human output. |
| `-v`, `--verbose` | count | `0` | Increase detail level. |
| `--json` | bool | `false` | JSON output for scripts. |
| `--plain` | bool | `false` | Stable `key=value` output. |
| `--no-color` | bool | `false` | Disable ANSI colors. |
| `--no-input` | bool | `false` | Disable prompts. |
| `-n`, `--dry-run` | bool | `false` | Plan operation only. |
| `-f`, `--force` | bool | `false` | Skip confirmation prompts. |
| `--enqueue` | bool | `false` | Write operation envelopes to jobs directory. |

## Subcommand Semantics

| Command | Idempotence | State Changes |
|---|---|---|
| `init` | Idempotent with `--force` | Creates project config + ledger/jobs paths. |
| `auth connect` | Idempotent updates | Updates auth metadata, optional token import. |
| `auth import-token` | Idempotent updates | Writes secret file and metadata reference. |
| `auth login` | Idempotent updates | Stores OAuth metadata and emits auth URL. |
| `auth exchange-code` | Idempotent updates | Exchanges OAuth code and stores tokens. |
| `auth whoami` | Read-only (unless `--save-author`) | Optionally persists `author_urn`. |
| `auth status` | Read-only | None. |
| `auth revoke` | Idempotent | Deletes local auth metadata and known token files. |
| `post create` | Side-effect | Creates LinkedIn post; writes local post receipt ledger entry. |
| `post get` | Read-only | None. |
| `post list` | Read-only | None. |
| `post history` | Read-only | None. |
| `analytics get` | Read-only | None. |

## I/O Contract

- `stdout`:
  - Primary command result (`human`, `--json`, or `--plain`).
- `stderr`:
  - Errors, warnings, prompt context.
- TTY behavior:
  - Prompts only when stdin is a TTY.
  - Non-interactive side effects require `--force` or `--dry-run`.

## Exit Codes

- `0`: Success
- `1`: Generic failure
- `2`: Usage/validation error
- `3`: Config/state file error
- `4`: Not implemented integration path
- `5`: Auth required/missing auth state
- `6`: External request failure
- `7`: Confirmation required/canceled
- `130`: Interrupted (Ctrl-C)

## Safety Rules

- Side-effect command (`post create`):
  - Confirm interactively by default.
  - In non-interactive mode require `--force` (or use `--dry-run`).
- Secrets:
  - Never passed as plain token flags.
  - Import via `--token-file` or `--token-stdin`.
  - OAuth client secret via file/stdin/env, never echoed.

## Config + Env Rules

Precedence: `flags > env > project config > user config > system config`

Config files:
- System: `/etc/linkedin-cli/config.json`
- User: `${XDG_CONFIG_HOME:-~/.config}/linkedin-cli/config.json`
- Project: `.linkedin-cli/config.json` (or `--config`)

Important env vars:
- `LINKEDIN_CLI_PROFILE`
- `LINKEDIN_CLI_OUTPUT`
- `LINKEDIN_CLI_TOKEN_STORE`
- `LINKEDIN_CLI_SECRETS_DIR`
- `LINKEDIN_CLI_JOBS_DIR`
- `LINKEDIN_CLI_LEDGER_PATH`
- `LINKEDIN_CLI_NO_INPUT`
- `LINKEDIN_CLIENT_ID`
- `LINKEDIN_CLIENT_SECRET`
- `LINKEDIN_CLI_REDIRECT_URI`
- `NO_COLOR`

## Local State Defaults

- Token metadata: `${XDG_CONFIG_HOME:-~/.config}/linkedin-cli/tokens.json`
- Secret files: `${XDG_CONFIG_HOME:-~/.config}/linkedin-cli/secrets/<profile>/...`
- Jobs queue: `.linkedin-cli/jobs`
- Post receipt ledger: `.linkedin-cli/posts.jsonl`

## LinkedIn API Targets

- OAuth authorization URL:
  - `https://www.linkedin.com/oauth/v2/authorization`
- OAuth token exchange:
  - `https://www.linkedin.com/oauth/v2/accessToken`
- Create/get/list posts:
  - `https://api.linkedin.com/v2/ugcPosts`
- Engagement stats:
  - `https://api.linkedin.com/v2/socialActions/{targetUrn}`
- Profile discovery:
  - `https://api.linkedin.com/v2/userinfo` (preferred)
  - `https://api.linkedin.com/v2/me` (fallback)

## Completion Story

`linkedin-cli completion --shell bash|zsh|fish`

## Example Commands

```bash
# initialize local project state
python3 linkedin_cli.py init

# prepare OAuth auth URL (client secret from stdin)
printf '%s' "$LINKEDIN_CLIENT_SECRET" | python3 linkedin_cli.py auth login \
  --client-id "$LINKEDIN_CLIENT_ID" \
  --client-secret-stdin

# exchange callback code for tokens
python3 linkedin_cli.py auth exchange-code --code "$LINKEDIN_CODE"

# fetch profile and save inferred author urn
python3 linkedin_cli.py --json auth whoami --save-author

# dry-run publish operation
printf 'Shipping a new feature this week.' | python3 linkedin_cli.py -n --json post create --stdin

# publish for real (non-interactive)
printf 'Shipping a new feature this week.' | python3 linkedin_cli.py --force --json post create --stdin

# retrieve created post details
python3 linkedin_cli.py --json post get --post-urn "urn:li:ugcPost:123"

# view recent local post receipts
python3 linkedin_cli.py --json post history --limit 10

# fetch engagement analytics for a post
python3 linkedin_cli.py --json analytics get --post-urn "urn:li:ugcPost:123"
```
