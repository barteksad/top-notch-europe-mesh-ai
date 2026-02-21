---
theme: default
title: "top-notch-europe-mesh-ai | Fundraising Deck"
info: |
  Revised for clean Slidev rendering and stronger investor narrative.
mdc: true
drawings:
  enabled: false
exportFilename: "top-notch-europe-mesh-ai-fundraising-deck"
---

---
layout: cover
---

# top-notch-europe-mesh-ai

Repo-to-distribution engine for hackathon teams.

- One command: research -> brief -> Instagram + LinkedIn + pitch deck
- Built at HackEurope in Feb 2026 by a 2-person team
- Open source: https://github.com/barteksad/top-notch-europe-mesh-ai

<!--
Evidence:
- Workflow and channels from social/README.md
- Repository URL and hackathon framing from current deck + README context
-->

---
layout: two-cols
---

# Team

## Builders who ship

- TomekNocon: 9 commits
- Bartek Sadlej: 4 commits
- 13 commits across 2026-02-21 to 2026-02-22

::right::

## Why this team can win

- Combined skills in automation workflows, media generation, and distribution tooling
- Shipped Instagram flow first, then LinkedIn and pitch deck paths
- Built both command UX (`/go-to-market`) and generation scripts

<!--
Evidence:
- git shortlog -sn HEAD
- git log dates and commit messages
- social/commands/go-to-market.md and social/scripts/
-->

---
layout: default
---

# Problem

<v-clicks>

- Hackathon projects lose momentum after demo day because promotion is manual.
- Builders rewrite the same project story for each channel from scratch.
- Generating visuals, captions, and investor decks takes more time than shipping code.
- Result: strong technical projects stay invisible after launch.

</v-clicks>

<!--
Evidence:
- Problem statement in README.md and social/README.md

Assumptions to confirm:
- Exact post-hackathon drop-off rate by segment
-->

---
layout: two-cols
---

# Solution

## Unified workflow

1. `/go-to-market` analyzes repository context once.
2. A shared brief becomes a reusable source of truth.
3. Channel skills generate channel-native assets and copy.

::right::

## What ships today

- Instagram media generation + publishing path
- LinkedIn strategy + CLI posting flow
- Slidev investor deck generation from the same brief
- Reusable Python generators for Imagen and Veo models

<!--
Evidence:
- social/README.md usage and component docs
- social/scripts/generate_image.py
- social/scripts/generate_video.py
- social/commands/go-to-market.md
-->

---
layout: default
---

# Why Now

| Shift | Why it matters |
| --- | --- |
| Generative media APIs are usable in production | Small teams can ship campaign-ready assets fast |
| Agent skills + CLI workflows are maturing | Multi-step GTM execution can run from one command |
| Hackathon output keeps growing | More builders need post-demo distribution support |

- Timing thesis: distribution tooling is becoming a core part of developer tooling.

<!--
Assumptions to confirm:
- External market trend sizes and growth rates
-->

---
layout: default
---

# Traction

- Active build velocity: 13 commits from 2 contributors, latest commit on 2026-02-22.
- Real generated artifacts already stored in `uploads/` (`.png` and `.mp4`).
- End-to-end architecture is implemented across research, generation, and channel skills.
- Single distribution command is documented and runnable (`social/commands/go-to-market.md`).

<!--
Evidence:
- git rev-list --count HEAD
- git shortlog -sn HEAD
- git log -1 --format with date
- uploads/* media files
- social/commands/go-to-market.md
-->

---
layout: two-cols
---

# Market

## Beachhead ICP

- Hackathon teams in the first 7-14 days after demo day
- Student founders and indie hackers launching MVPs
- Technical builders with low marketing bandwidth

::right::

## Expansion path

- Accelerator cohorts needing weekly launch/distribution packs
- Devtool teams converting release notes into multi-channel GTM content
- Agency and community operators supporting many small teams

<!--
Evidence:
- ICP direction inferred from README/social intent

Assumptions to confirm:
- Bottom-up market sizing and willingness to pay by segment
-->

---
layout: default
---

# Ask

- Proposed raise (draft): EUR 300k for 12 months runway.
- Objective: convert a hackathon prototype into a repeatable GTM engine for technical founders.

| Next milestones (6-12 months) | Target output |
| --- | --- |
| Productize brief + generation pipeline | Reliable multi-channel content packs |
| Add analytics feedback loop | Narrative-to-engagement tracking by channel |
| Run design-partner pilots | 20-30 teams using the workflow repeatedly |

- Draft use of funds: product engineering 55%, model/API spend 25%, GTM experiments 20%.

<!--
Assumptions to confirm:
- Raise amount and runway target
- Pilot volume target and milestone timing
-->
