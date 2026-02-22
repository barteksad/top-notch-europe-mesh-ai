# Social Plugin

Social media and fundraising toolkit for hackathon projects.

It supports:
- repo-aware brief generation,
- Instagram post/reel generation and publishing,
- LinkedIn post workflows,
- investor pitch deck generation from repository context.

## Prerequisites

- Python 3.10+
- `pip install -r social/scripts/requirements.txt`
- `pip install -r social/server/requirements.txt` in `social/server/.venv`
- Gemini API key (for AI media generation)
- Instagram Graph API credentials (for posting)

## Unified Environment Setup

From repository root:

```bash
cp .env.example .env
# fill values

./scripts/validate_env.sh --load --profile all
```

Run agents so they inherit env values:

```bash
./scripts/run_with_env.sh claude
./scripts/run_with_env.sh codex
```

Use `.env.local` for machine-specific overrides.

## Environment Variables

| Variable | Required for | Description |
|---|---|---|
| `GEMINI_API_KEY` | AI generation | Gemini key for image/video generation |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram posting | Graph API access token |
| `INSTAGRAM_USER_ID` | Instagram posting | Instagram Business account ID |
| `GITHUB_TOKEN` | Local media upload | Token used for GitHub upload flow |
| `GITHUB_REPO` | Local media upload | Repo in `owner/repo` format |
| `LINKEDIN_CLIENT_ID` | LinkedIn CLI auth | LinkedIn app client id |
| `LINKEDIN_CLIENT_SECRET` | LinkedIn CLI auth | LinkedIn app client secret |
| `LINKEDIN_CLI_REDIRECT_URI` | LinkedIn CLI auth | Redirect URI configured in LinkedIn app |

## Commands

- `/go-to-market` - End-to-end workflow: research repo -> build/update `.social/project-brief.json` -> distribute to selected channels.
- `/post-instagram` - Instagram-only flow for a single post/reel using the existing brief.

## Skills

- `go-to-market-pipeline`
- `instagram-content-strategy`
- `linkedin-cli`
- `repo-to-fundraising-pitchdeck`
- `social-md-changelog`

## Runtime Notes

When script paths are needed, resolve `SOCIAL_ROOT` like this:

```bash
SOCIAL_ROOT="${CLAUDE_PLUGIN_ROOT:-social}"
if [[ ! -f "$SOCIAL_ROOT/scripts/generate_image.py" && -f "$SOCIAL_ROOT/social/scripts/generate_image.py" ]]; then
  SOCIAL_ROOT="$SOCIAL_ROOT/social"
fi
```

This supports both plugin roots:
- repository root plugin install,
- legacy `social/` plugin install.
