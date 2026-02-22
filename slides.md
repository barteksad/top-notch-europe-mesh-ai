---
theme: default
title: "TopNotchEuropeMeshAI | Fundraising Deck"
info: |
  Generated with repo-to-fundraising-pitchdeck.
mdc: true
drawings:
  enabled: false
exportFilename: "topnotcheuropemeshai-fundraising-deck"
---

---

---
layout: cover
---

# TopNotchEuropeMeshAI

- A cross-agent go-to-market copilot that turns software repos into launch-ready social campaigns and investor materials from a single prompt.
- Stage: pre-seed
- Repository: https://github.com/barteksad/top-notch-europe-mesh-ai
- Target raise: EUR 500,000

<!--
Evidence:
- README.md defines the product as a cross-platform social workflow plugin and skills pack for Claude Code and Codex.
- .claude-plugin/plugin.json ships plugin version 1.2.0 with repository and marketplace metadata.
- social/commands/go-to-market.md documents an end-to-end flow from repo research to Instagram, LinkedIn, and pitch deck output.

Assumptions to confirm:
- Raise amount and runway are draft placeholders pending founder confirmation.
-->

---

---
layout: default
---

# Team

- **Builders who already shipped a working cross-agent distribution stack.**
- Core contributors visible in git history: TomekNocon and Bartek Sadlej.
- Team shipped both source workflows and distributable bundles for Claude marketplace and Codex skills.
- Execution spans product workflow design, AI media generation scripts, and publishing infrastructure.

<!--
Evidence:
- git shortlog -sn HEAD shows two active contributors.
- scripts/build_universal_packages.sh builds and versions both Claude and Codex distribution bundles.
- dist/ contains packaged artifacts including topnotch-social-claude-marketplace-v1.2.0.tar.gz and topnotch-social-codex-skills-v1.2.0.tar.gz.

Assumptions to confirm:
- Founder backgrounds, prior exits, and role split are not yet documented in the repository.
-->

---

---
layout: default
---

# Problem

- **European builders can build fast, but distribution and fundraising execution blocks launch momentum.**
- Many AI prototypes and side projects stop after a demo because go-to-market work is fragmented and time-consuming.
- Builders are forced into marketer, salesperson, and fundraiser roles without repeatable systems.
- Customer research, launch content, and investor narrative creation become separate overhead projects.

<!--
Evidence:
- Founder narrative provided in the pitch text explicitly states this pain pattern and stalled project outcomes.
- The repository focuses on solving this exact gap through commands that automate social distribution and deck generation.

Assumptions to confirm:
- No quantified funnel-drop or conversion benchmarks are currently captured in-repo.
-->

---

---
layout: default
---

# Solution

- **One prompt activates a multi-skill agent workflow that turns a repo into a launch system.**
- The `/go-to-market` command builds a reusable project brief and routes output to Instagram, LinkedIn, and investor deck generation.
- Gemini-powered scripts generate campaign media assets (image and video) from project context.
- Publishing is connected to execution channels: LinkedIn CLI for posting and Instagram MCP server for photo/reel publishing.
- Workflow state is designed to persist in project files (`.social/project-brief.json` and SOCIAL.md) for reruns and progress tracking.

<!--
Evidence:
- social/commands/go-to-market.md defines the multi-channel pipeline and deck generation steps.
- social/scripts/generate_image.py and social/scripts/generate_video.py implement Gemini API media generation.
- social/skills/linkedin-cli/scripts/linkedin_cli.py implements OAuth, post create/get/list, and analytics commands.
- social/server/server.py exposes `post_photo` and `post_reel` MCP tools for Instagram Graph API publishing.
- skills/ contains six top-level skill directories.

Assumptions to confirm:
- OpenAI Codex and Cursor distribution readiness is inferred from Codex packaging and workflow docs; direct Cursor install docs need explicit confirmation.
- End-to-end autopublishing depends on valid third-party credentials and account permissions.
-->

---

---
layout: default
---

# Why Now

- **AI coding output is rising faster than founder go-to-market capacity, creating a distribution automation gap.**
- Builder workflows can now produce prototypes quickly, but launch orchestration is still mostly manual.
- LLM APIs and MCP-compatible tooling make it feasible to automate media generation, posting, and investor narrative output in one system.
- Cross-agent packaging (Claude plugin plus Codex skills bundles) enables immediate distribution where builders already work.

<!--
Evidence:
- Repository ships both plugin and skills distribution channels with mirrored workflow content.
- go-to-market and channel-specific commands codify an end-to-end launch path from repo context.

Assumptions to confirm:
- Market urgency and timing drivers are based on observed builder behavior; external trend citations are not yet attached.
- Cursor channel demand is assumed from adjacent Codex/Cursor usage patterns.
-->

---

---
layout: default
---

# Traction

- **Early execution proof: functioning product surface, packaged releases, and rapid iteration.**
- 15 commits in current history with latest commit on 2026-02-22 focused on distribution and packaging.
- Versioned release artifacts are already generated for both marketplace and skills-only installs.
- Workflow spans repo analysis, media generation, social posting, and pitch deck generation from a single command surface.
- Six reusable skills are bundled and mirrored for distribution consistency.

<!--
Evidence:
- git rev-list --count HEAD returns 15; latest commit subject: feat: distribution and package.
- dist/ includes v1.2.0 tarballs for Claude marketplace and Codex skills.
- README.md and social/README.md document supported workflow outcomes and required channels.
- SOCIAL.md exists with ledger conventions.
- skills/ top-level folders confirm six packaged skills.
- Repository footprint: ~210 files scanned.
- Most common file extensions: .md (147), .json (17), .py (11), .yaml (10), .tsx (9).
- Build/runtime manifests detected: requirements.txt.
- Git commits in history: 15.
- Latest commit date: 2026-02-22.

Assumptions to confirm:
- No production usage, retention, or revenue metrics are stored in the repository yet.
- No customer interview or pilot conversion data is currently documented.
-->

---

---
layout: default
---

# Market

- **Wedge: builders shipping AI projects who need a fast path from prototype to distribution.**
- Initial users are hackathon teams, side-project builders, and early founders who can build but lack GTM capacity.
- Product starts with social launch and fundraising narrative, then expands into repeat campaign operations via project files.
- Cross-agent compatibility enables adoption across existing builder tools instead of forcing a new platform.
- Expansion path: from launch assistant into ongoing growth operating system for technical founders.

<!--
Evidence:
- README and social docs repeatedly target hackathon projects and developer workflows.
- Pipeline artifacts (`.social/project-brief.json`, SOCIAL.md, generated media/deck assets) are structured for repeat operation.

Assumptions to confirm:
- TAM/SAM/SOM quantification is not yet included and should be added with external market research.
- Conversion from hackathon users to paying startup customers remains to be validated.
-->

---

---
layout: default
---

# Ask

- Raise amount: EUR 500,000
- Runway target: 18 months
- **Raise a focused pre-seed round to validate repeatable demand and scale distribution.**
- Target raise: EUR 500,000 for 18 months runway.
- Primary goal: prove repeatable prototype-to-distribution outcomes with design partners.
- Next-round trigger: clear retention and conversion signal from pilot to paid usage.

<!--
Evidence:
- Current repository indicates pre-seed stage product execution but no monetization metrics.
- Existing workflow architecture supports milestone-based validation once users are onboarded.

Assumptions to confirm:
- Final raise amount, runway target, and milestone thresholds require founder approval.
- Pilot volume and paid conversion targets are planning assumptions, not observed metrics.
-->
