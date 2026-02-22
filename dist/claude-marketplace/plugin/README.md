<p align="center">
  <img src="assets/topnotch-europe-mesh-ai-logo.png" alt="TopNotchEuropeMeshAI logo" width="280" />
</p>

<h1 align="center">TopNotchEuropeMeshAI</h1>

Cross-platform social workflow plugin and skills pack for Claude Code and Codex.

## What This Repository Ships

- Claude plugin: `social`
- Claude marketplace metadata: `.claude-plugin/marketplace.json`
- Codex skills pack: `skills/`
- Canonical social workflow source: `social/`

The social workflow turns a repo into:
- a reusable project brief (`.social/project-brief.json`),
- Instagram content and publishing actions,
- LinkedIn draft/publish workflows,
- an 8-slide fundraising pitch deck draft.

## Repository Layout

```text
.
├── .claude-plugin/
│   ├── marketplace.json
│   └── plugin.json
├── .mcp.json
├── codex/
│   └── INSTALL.md
├── scripts/
│   ├── sync_social_skills.sh
│   ├── validate_universal_packages.sh
│   └── build_universal_packages.sh
├── skills/                  # Codex-distributed mirror (generated)
└── social/                  # Canonical source for commands, MCP, and skill content
    ├── .claude-plugin/plugin.json
    ├── .mcp.json
    ├── commands/
    ├── scripts/
    ├── server/
    └── skills/
```

## Install

### Claude Code

Add this repo as a marketplace source:

```bash
claude --plugin add-marketplace barteksad/top-notch-europe-mesh-ai
```

Install the plugin from that marketplace:

```bash
claude --plugin install social@topnotch-social-marketplace
```

For local development, install directly from a local clone:

```bash
claude --plugin install --local /absolute/path/to/top-notch-europe-mesh-ai
```

### Codex

Tell Codex to fetch and follow:

```text
https://raw.githubusercontent.com/barteksad/top-notch-europe-mesh-ai/main/codex/INSTALL.md
```

Or read local instructions in `codex/INSTALL.md`.

## Local Prerequisites

- Python 3.10+
- `jq`, `rsync`, `tar`
- Python dependencies:

```bash
python3 -m pip install -r social/scripts/requirements.txt
python3 -m venv social/server/.venv
social/server/.venv/bin/pip install -r social/server/requirements.txt
```

## Environment Variables

| Variable | Required for |
|---|---|
| `GEMINI_API_KEY` | AI media generation |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram publish |
| `INSTAGRAM_USER_ID` | Instagram publish |
| `GITHUB_TOKEN` | Upload local media before Instagram publish |
| `GITHUB_REPO` | Upload local media before Instagram publish |
| `LINKEDIN_CLIENT_ID` | LinkedIn CLI auth |
| `LINKEDIN_CLI_REDIRECT_URI` | LinkedIn CLI auth |

## Maintainer Workflow

Treat `social/` as source of truth.

1. Edit plugin source files only under `social/`.
2. Mirror skills into `skills/`:

```bash
./scripts/sync_social_skills.sh --validate
```

3. Validate cross-platform packaging:

```bash
./scripts/validate_universal_packages.sh
```

4. Build distributable bundles:

```bash
./scripts/build_universal_packages.sh
```

Generated artifacts are written to `dist/`.

## Distribution and Release Checklist

1. Update version in:
- `.claude-plugin/plugin.json`
- `social/.claude-plugin/plugin.json`
- `.claude-plugin/marketplace.json` (`metadata.version` and plugin `version`)

2. Run:

```bash
./scripts/build_universal_packages.sh
```

3. Verify artifacts:
- `dist/topnotch-social-claude-marketplace-v<version>.tar.gz`
- `dist/topnotch-social-codex-skills-v<version>.tar.gz`
- compatibility aliases:
  - `dist/topnotch-social-claude-marketplace.tar.gz`
  - `dist/topnotch-social-codex-skills.tar.gz`
  - `dist/topnotch-social-agent-skills.tar.gz`

4. Tag and publish release on GitHub with built artifacts attached.

## License

Apache-2.0. See `LICENSE`.
