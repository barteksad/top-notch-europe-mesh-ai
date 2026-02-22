---
name: social-md-changelog
description: Maintain SOCIAL.md as an append-only changelog for all repository social actions performed by an agent, including drafting, publishing, repurposing, engagement, and analytics updates. Use when creating social content, publishing to LinkedIn/Instagram/X, reviewing what was posted before, reusing prior post patterns, or making social-related commits that should be tagged with `social(...)`.
---

# SOCIAL.md Changelog

Track social execution with the same rigor as engineering changes.

## Runtime Path Helper

Use this helper before running script commands:

```bash
SOCIAL_ROOT="${CLAUDE_PLUGIN_ROOT:-social}"
if [[ ! -f "$SOCIAL_ROOT/skills/social-md-changelog/scripts/social_log.py" && -f "$SOCIAL_ROOT/social/skills/social-md-changelog/scripts/social_log.py" ]]; then
  SOCIAL_ROOT="$SOCIAL_ROOT/social"
fi
```

Keep one `SOCIAL.md` ledger in the repository root and tie every social action to artifacts and commits.

## Workflow

### 1. Initialize the ledger once

Run at repository setup:

```bash
python3 $SOCIAL_ROOT/skills/social-md-changelog/scripts/social_log.py init --path SOCIAL.md
```

If `SOCIAL.md` already exists, keep existing content and append new entries only.

### 2. Read recent history before writing new content

Load recent context to avoid repeating hooks, claims, and CTA language:

```bash
python3 $SOCIAL_ROOT/skills/social-md-changelog/scripts/social_log.py recent --path SOCIAL.md --limit 10
```

### 3. Append an entry after every social action

Log each meaningful action (draft, review, publish, repurpose, analytics snapshot, campaign action):

```bash
python3 $SOCIAL_ROOT/skills/social-md-changelog/scripts/social_log.py add \
  --path SOCIAL.md \
  --platform linkedin \
  --action publish \
  --status published \
  --title "Launch post for SOCIAL.md" \
  --summary "Published launch post announcing the SOCIAL.md workflow." \
  --content-file /tmp/linkedin_post.txt \
  --link "landing=https://v0-social-md-website.vercel.app/#" \
  --link "post=https://www.linkedin.com/feed/update/..." \
  --asset "/tmp/linkedin_post_image.png" \
  --commit "abc1234" \
  --tag launch \
  --tag linkedin
```

Prefer `--content-file` for published text so formatting is preserved exactly as posted.

### 4. Use social commit conventions for related repo changes

For code or content files created for social operations, use:

- Subject format: `social(<platform>): <verb> <topic>`
- Examples:
  - `social(linkedin): publish launch post`
  - `social(instagram): add reel caption variants`
- Commit trailer in body: `Social-Log: <entry-id>`

Create the commit after logging so the entry ID can be referenced.

### 5. Keep history append-only

Do not delete or rewrite older entries. If corrections are needed, append a new `correction` or `follow-up` entry and link the earlier entry in notes.

## Required Entry Data

Capture these fields for each log entry:

- UTC timestamp
- platform
- action
- summary
- status
- full post content (if the action produced content)
- links (landing URL, post URL, analytics URL, docs)
- related commit hashes
- tags

Use `references/logging-rules.md` for allowed action taxonomy and checklist.
Use `references/social-entry-template.md` for manual entries when script usage is not possible.

## Resources

- `scripts/social_log.py`: initialize ledger, append entries, inspect recent activity.
- `references/logging-rules.md`: action taxonomy, required fields, commit linkage rules.
- `references/social-entry-template.md`: manual markdown template compatible with this skill.
