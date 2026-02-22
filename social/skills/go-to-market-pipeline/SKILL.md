---
name: go-to-market-pipeline
description: Execute an end-to-end go-to-market workflow for a hackathon or software project. Use when the user asks to research a repository, build or update `.social/project-brief.json`, create distribution-ready Instagram or LinkedIn content, or generate an investor pitch deck from project artifacts.
---

# Go To Market Pipeline

Run a single workflow: research the project, build a reusable brief, and distribute content across selected channels.

## Working Paths

Use this variable in shell snippets so the workflow works in both Claude plugin and Codex/Cursor repo mode:

```bash
SOCIAL_ROOT="${CLAUDE_PLUGIN_ROOT:-social}"
if [[ ! -f "$SOCIAL_ROOT/scripts/generate_image.py" && -f "$SOCIAL_ROOT/social/scripts/generate_image.py" ]]; then
  SOCIAL_ROOT="$SOCIAL_ROOT/social"
fi
```

If the current working directory is not the repository root, set `SOCIAL_ROOT` to an absolute path.

## Phase 1: Research and Brief

1. Locate project input
- Use argument path/URL when provided.
- If URL is provided, clone to `/tmp/research-repo`.
- If nothing is provided, use current directory.

2. Extract repository evidence
- Read `README*`, manifests (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, etc.), docs, and recent git history.
- Record direct facts as evidence, not assumptions.

3. Load or initialize brief
- Prefer existing `.social/project-brief.json`.
- If missing, initialize from `$SOCIAL_ROOT/references/project-brief-template.json`.
- Preserve existing user-provided fields when updating.

4. Fill critical gaps with user input
- Problem + target user.
- Hackathon context.
- Preferred content angle.
- Ask one question at a time.

5. Optional market research
- Ask whether to enrich with competitor, trend, and market-size research.
- Add source-backed findings under market and why-now sections.

6. Save brief
- Write `.social/project-brief.json`.
- Print summary: filled sections, missing sections, evidence vs assumptions.

## Phase 2: Distribution

Ask which channels to run: Instagram, LinkedIn, Pitch deck, or all.

### Instagram

1. Choose content angle.
2. Choose media mode: AI-generated image/video or user-provided media.
3. Generate media if needed:

```bash
GEMINI_API_KEY="$GEMINI_API_KEY" python3 "$SOCIAL_ROOT/scripts/generate_image.py" \
  --prompt "<crafted prompt>" \
  --output /tmp/instagram_post_image.png \
  --model imagen \
  --aspect-ratio 1:1
```

```bash
GEMINI_API_KEY="$GEMINI_API_KEY" python3 "$SOCIAL_ROOT/scripts/generate_video.py" \
  --prompt "<crafted prompt>" \
  --output /tmp/instagram_post_video.mp4 \
  --model veo3 \
  --aspect-ratio 9:16 \
  --duration 8
```

4. Draft caption with hook, story, CTA, and hashtags.
5. Ask for explicit approval before posting.
6. Post through Instagram MCP tools and return media id + URL.

### LinkedIn

1. Choose content angle and format (text or text+image).
2. Generate image if requested:

```bash
GEMINI_API_KEY="$GEMINI_API_KEY" python3 "$SOCIAL_ROOT/scripts/generate_image.py" \
  --prompt "<crafted prompt>" \
  --output /tmp/linkedin_post_image.png \
  --model nanobanana-pro \
  --aspect-ratio 4:3
```

3. Draft post with short paragraphs, first-line hook, and 3-5 hashtags.
4. Ask for approval.
5. Publish with LinkedIn CLI:

```bash
python3 "$SOCIAL_ROOT/skills/linkedin-cli/scripts/linkedin_cli.py" post create \
  --text "<the post text>" \
  --visibility public
```

### Pitch Deck

1. Map brief to the 8-slide structure.
2. Generate draft:

```bash
python3 "$SOCIAL_ROOT/skills/repo-to-fundraising-pitchdeck/scripts/generate_slidev_pitchdeck.py" \
  --brief .social/project-brief.json \
  --out slides.md \
  --repo-path .
```

3. Review assumptions and evidence notes.
4. Export PDF when requested.

## Guardrails

- Do not invent traction, revenue, user counts, or market numbers.
- Keep claims tied to repository evidence or user-confirmed inputs.
- Confirm before any side-effect action (publishing or external writes).
- Reuse the existing brief instead of re-asking for known context.
