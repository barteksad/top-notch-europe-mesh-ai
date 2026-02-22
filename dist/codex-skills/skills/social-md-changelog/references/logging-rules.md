# SOCIAL.md Logging Rules

## Required Fields

Every entry must include:

- `id`: `SOC-YYYYMMDD-NNN` (daily sequence)
- `timestamp`: UTC ISO-8601 (`...Z`)
- `platform`: where the action happened (`linkedin`, `instagram`, `x`, `newsletter`, etc.)
- `action`: one canonical action from the taxonomy below
- `summary`: one-sentence outcome
- `status`: current lifecycle state

Add these whenever available:

- full post content (`### Content` block)
- links (`landing`, `post`, `analytics`, `repo`, or docs)
- related assets (images/videos/files)
- related commits
- tags for queryability
- notes for follow-up context

## Action Taxonomy

Use one of these action names:

- `draft`
- `review`
- `schedule`
- `publish`
- `repurpose`
- `comment-campaign`
- `dm-outreach`
- `analytics-snapshot`
- `correction`
- `follow-up`

If none fits, use a precise custom action and keep wording stable across entries.

## Status Vocabulary

Prefer these statuses:

- `draft`
- `ready`
- `scheduled`
- `published`
- `blocked`
- `failed`
- `archived`

## Commit Linkage

For repository changes tied to social operations:

- Use commit subject prefix: `social(<platform>): ...`
- Add trailer: `Social-Log: <entry-id>`
- Add commit hash back into SOCIAL.md entry once commit exists

## Entry Lifecycle

- Keep SOCIAL.md append-only.
- Never rewrite published content entries.
- Append new entries for updates instead of mutating old entries.
- Use `correction` or `follow-up` to supersede previous records.

## Quality Checklist

Before closing a social task, verify:

- entry exists for this action
- summary states a clear outcome
- post text is preserved exactly (if published)
- landing/post URLs are recorded
- commit hash is linked when files changed
