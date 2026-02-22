# Slidev Playbook For Fundraising Decks

## Sources

- Slidev repository: `https://github.com/slidevjs/slidev`
- Getting started: `https://sli.dev/guide/`
- CLI reference: `https://sli.dev/builtin/cli`
- Syntax guide: `https://sli.dev/guide/syntax`
- Layouts: `https://sli.dev/guide/layout` and `https://sli.dev/builtin/layouts`
- Exporting: `https://sli.dev/guide/exporting`

## Core Commands

Create a new Slidev project:

```bash
npm init slidev
```

Serve the deck locally:

```bash
slidev slides.md
```

Build a shareable SPA:

```bash
slidev build
```

Export files for sharing:

```bash
slidev export --format pdf
slidev export --format pptx
slidev export --format png
```

## Authoring Basics

- `slides.md` is the default entry file.
- Separate slides with `---`.
- Use YAML headmatter on the first slide for global config.
- Use per-slide frontmatter blocks for layout and behavior.

Example:

```md
---
theme: default
title: My Fundraising Deck
---

---
layout: cover
---

# Company Name
```

## Recommended Layout Strategy

- Use `cover` for slide 1.
- Use `default` for most slides.
- Use `two-cols` for dense comparison slides when needed.
- Avoid frequent layout switching unless it improves comprehension.

## Recommended Components

- Use `<v-clicks>` for progressive bullet reveal.
- Use `v-click` for single-item reveal.
- Avoid animation-heavy transitions that distract from the pitch.

## Suggested Deck Conventions

- Keep 1 claim per slide.
- Keep 3 to 5 bullets per slide.
- Put raw details in presenter notes, not body copy.
- Keep totals and units explicit for market and ask slides.

## Export Notes

- Install Playwright for PDF/PPTX/PNG export:

```bash
npm i -D playwright-chromium
```

- Use `slidev export --with-clicks` only if click states are important in output.
- Use `slidev export --range` to generate partial investor variants.

## Repository Signals To Reuse In Slides

- language and stack inferred from manifests
- key feature folders and shipped demos
- commit history and release cadence
- integration points and API boundaries

Use these as objective proof in team, solution, and traction slides.
