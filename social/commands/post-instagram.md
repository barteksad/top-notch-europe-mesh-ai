---
name: post-instagram
description: Generate and publish an Instagram post for the current project using the existing project brief.
argument-hint: "[optional path to .social/project-brief.json]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
  - mcp__instagram__post_photo
  - mcp__instagram__post_reel
---

# Post Instagram

Create and publish a single Instagram post (image or reel) using the repository brief.

## Step 1: Resolve brief and runtime paths

Use this runtime helper before any script commands:

```bash
SOCIAL_ROOT="${CLAUDE_PLUGIN_ROOT:-social}"
if [[ ! -f "$SOCIAL_ROOT/scripts/generate_image.py" && -f "$SOCIAL_ROOT/social/scripts/generate_image.py" ]]; then
  SOCIAL_ROOT="$SOCIAL_ROOT/social"
fi
```

Brief path priority:
1. Command argument if provided.
2. `.social/project-brief.json` in the current repository.

If no brief exists, ask the user to run `/go-to-market` first, or gather minimal context manually (project name, one-liner, audience, content angle).

## Step 2: Pick angle and media mode

Ask the user:
1. Which content angle to use.
2. Media mode:
- AI-generated image (1:1)
- AI-generated video reel (9:16)
- User-provided media path

## Step 3: Generate media when requested

For image:

```bash
GEMINI_API_KEY="$GEMINI_API_KEY" python3 "$SOCIAL_ROOT/scripts/generate_image.py" \
  --prompt "<crafted prompt>" \
  --output /tmp/instagram_post_image.png \
  --model imagen \
  --aspect-ratio 1:1
```

For video:

```bash
GEMINI_API_KEY="$GEMINI_API_KEY" python3 "$SOCIAL_ROOT/scripts/generate_video.py" \
  --prompt "<crafted prompt>" \
  --output /tmp/instagram_post_video.mp4 \
  --model veo3 \
  --aspect-ratio 9:16 \
  --duration 8
```

## Step 4: Draft caption

Use brief context to write a caption with:
- a hook in the first sentence,
- short project story,
- a clear call to action,
- 15-20 relevant hashtags.

Show caption and media choice to the user for explicit approval before posting.

## Step 5: Publish

If approved:
- Use `post_photo` for images.
- Use `post_reel` for videos.

Return:
- media type,
- media id,
- resulting Instagram URL,
- caption used.

## Step 6: Log action

If `SOCIAL.md` exists, append a social log entry with the platform (`instagram`), action (`publish`), and produced links.
