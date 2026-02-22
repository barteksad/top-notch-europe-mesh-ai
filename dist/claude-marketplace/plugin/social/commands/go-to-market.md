---
name: go-to-market
description: Full go-to-market pipeline for your hackathon project. Researches your repo, builds a project brief, then walks you through posting to Instagram, LinkedIn, and generating a pitch deck — all from one command.
argument-hint: "[repo path or GitHub URL]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
  - WebSearch
  - WebFetch
  - mcp__instagram__post_photo
  - mcp__instagram__post_reel
---

# Go To Market — Research, Create, Distribute

One command to go from repo to live content across all channels. This command:
1. **Researches** your project and builds a unified brief (`.social/project-brief.json`)
2. **Distributes** content to Instagram, LinkedIn, and generates a pitch deck

The brief is the single source of truth — each channel reads from it instead of re-asking for context.

Set a runtime path helper once before running any script commands:

```bash
SOCIAL_ROOT="${CLAUDE_PLUGIN_ROOT:-social}"
if [[ ! -f "$SOCIAL_ROOT/scripts/generate_image.py" && -f "$SOCIAL_ROOT/social/scripts/generate_image.py" ]]; then
  SOCIAL_ROOT="$SOCIAL_ROOT/social"
fi
```

---

## Phase 1: Research & Brief

### Step 1: Locate the Project

- If the user provided an argument, check whether it's a **local path** or a **GitHub URL**.
  - If it's a GitHub URL, clone it to `/tmp/research-repo` and work from there.
  - If it's a local path, use that directory.
- If no argument was provided, use the current working directory.
- Verify the directory contains source code (look for README.md, package.json, pyproject.toml, go.mod, Cargo.toml, or similar).

### Step 2: Extract Facts from the Repository

Read the following files (whichever exist) and extract project context:

- **README.md** (or README.rst, README.txt) — project name, description, features, usage
- **package.json / pyproject.toml / go.mod / Cargo.toml / build.gradle** — project name, dependencies, tech stack
- **docs/** directory — any additional documentation
- **Recent git log** (`git log --oneline -20`) — team members, build velocity, recent activity
- **Git contributors** (`git shortlog -sn --no-merges`) — team composition

For each piece of information extracted, mark it as `evidence` (directly from repo artifacts).

Fill in these brief sections from repo data:
- `meta.repo_url` — from git remote
- `project.name` — from manifest or README
- `project.description` — from README first paragraph
- `project.tech_stack` — from dependencies and file types
- `project.key_features` — from README feature lists
- `team.members` — from git contributors
- `narrative.traction.bullets` — from commit count, recency, contributor count

### Step 3: Check for Existing Brief

- Look for `.social/project-brief.json` in the project directory.
- If found, load it as the base. **Do not overwrite fields that already have user-provided values** — only fill in empty fields or add new evidence.
- If not found, start from the template at `references/project-brief-template.json`.

### Step 4: Fill Gaps with User Input

Present what was auto-extracted in a summary, then use AskUserQuestion to fill in critical fields that couldn't be inferred:

**Always ask (if not already filled):**
1. "What problem does this project solve and for whom?" — fills `narrative.problem`, `audience.target_users`, `audience.pain_points`
2. "What's the hackathon context?" (name, theme, prize category, build time, team members) — fills `hackathon.*`
3. "What's the main angle or story you want to highlight in content?" — fills `content_angles`

**Ask only if relevant and empty:**
4. "What's your one-liner pitch?" — fills `project.one_liner`
5. "What stage is the project?" (hackathon / pre-seed / seed / growth) — fills `project.stage`
6. "Are you fundraising? If so, how much and what milestones?" — fills `fundraising.*`

Mark user-provided answers as `evidence` when they state facts, or `assumptions` when they express goals or projections.

### Step 5: Optional Web Research

Ask the user: "Want me to research competitors, market size, and trends to strengthen your narrative?"

If yes:
- Use WebSearch to find competitors, market size estimates, and recent trends related to the project's domain.
- Add findings to `narrative.market` (market size, competitors) and `narrative.why_now` (trends, timing).
- Tag all web-sourced data as `evidence` with source URLs.

If no, skip this step.

### Step 6: Save the Brief

1. Set `meta.created_at` to the current ISO timestamp (or keep existing if updating).
2. Set `meta.updated_at` to the current ISO timestamp.
3. Write the completed brief to `.social/project-brief.json` in the project directory.
4. Print a summary to the user:
   - **Filled sections** — list sections that have content
   - **Gaps remaining** — list sections still empty or marked as assumptions
   - **Evidence vs. assumptions** — count of each

---

## Phase 2: Content Distribution

After the brief is saved, present the user with a distribution menu. They can pick which channels to activate, or run them all.

### Step 7: Choose Distribution Channels

Use AskUserQuestion with multi-select:

**"Which channels do you want to publish to?"**
- **Instagram** — Generate media (AI image or video) + caption, post to Instagram
- **LinkedIn** — Write a professional post, publish to LinkedIn
- **Pitch Deck** — Generate an 8-slide investor pitch deck (Slidev → PDF)

The user can select one, two, or all three. Execute the selected channels in the order below. Between each channel, confirm with the user before proceeding to the next.

### Step 8: Instagram (if selected)

Read `.social/project-brief.json` and use the `instagram-content-strategy` skill. Follow these steps:

1. **Pick a content angle** — Use `content_angles` from the brief. Ask which angle to use if multiple exist.

2. **Choose media type** — Ask the user:
   - **Generate with AI** → then ask Image (1:1, Imagen 4) or Video (9:16, Veo 3)
   - **Provide my own** → user supplies a file path

3. **Generate media** (if AI-generated):
   - Craft a generation prompt from `project`, `narrative.problem`, `narrative.solution`
   - For images:
     ```bash
     GEMINI_API_KEY="$GEMINI_API_KEY" python3 $SOCIAL_ROOT/scripts/generate_image.py \
       --prompt "<crafted prompt>" \
       --output /tmp/instagram_post_image.png \
       --model imagen \
       --aspect-ratio 1:1
     ```
   - For videos:
     ```bash
     GEMINI_API_KEY="$GEMINI_API_KEY" python3 $SOCIAL_ROOT/scripts/generate_video.py \
       --prompt "<crafted prompt>" \
       --output /tmp/instagram_post_video.mp4 \
       --model veo3 \
       --aspect-ratio 9:16 \
       --duration 8
     ```

4. **Craft caption** — Use brief context (`project.one_liner`, `hackathon`, `narrative.problem.headline`, `meta.repo_url`). Include hook, story, CTA, 15-20 hashtags.

5. **Present draft** to user for approval or edits.

6. **Post** — Use `post_photo` or `post_reel` MCP tools. Share result with Media ID and link.

### Step 9: LinkedIn (if selected)

Read `.social/project-brief.json` and use the `linkedin-cli` skill. Follow these steps:

1. **Pick a content angle** — Use `content_angles` from the brief. Can use a different angle than Instagram.

2. **Choose post format** — Ask:
   - **Text post** (highest organic reach)
   - **Text + Image** (AI-generated or user-provided, 4:3 aspect ratio)

3. **Generate image** (if requested):
   ```bash
   GEMINI_API_KEY="$GEMINI_API_KEY" python3 $SOCIAL_ROOT/scripts/generate_image.py \
     --prompt "<crafted prompt>" \
     --output /tmp/linkedin_post_image.png \
     --model nanobanana-pro \
     --aspect-ratio 4:3
   ```

4. **Craft LinkedIn post** — Use brief context (`project`, `audience`, `narrative.*`, `hackathon`, `meta.repo_url`, `meta.website`). Follow LinkedIn best practices:
   - Hook in first line (shows before "...see more")
   - Short paragraphs, line breaks between ideas
   - Professional but human tone, first person
   - Under 1300 characters for best engagement
   - 3-5 hashtags only

5. **Present draft** to user for approval or edits.

6. **Post** — Use LinkedIn CLI:
   ```bash
   python3 $SOCIAL_ROOT/skills/linkedin-cli/scripts/linkedin_cli.py post create \
     --text "<the post text>" \
     --visibility public
   ```

### Step 10: Pitch Deck (if selected)

Read `.social/project-brief.json` and use the `repo-to-fundraising-pitchdeck` skill. Follow these steps:

1. **Read required references**:
   - `references/pitch-framework-borys-musielak.md`
   - `references/slidev-playbook.md`

2. **Map brief to 8-slide framework**:
   - `brief.project` → Slide 1 (Company + one-line pitch)
   - `brief.team` → Slide 2 (Team)
   - `brief.narrative.problem` → Slide 3 (Problem)
   - `brief.narrative.solution` → Slide 4 (Solution)
   - `brief.narrative.why_now` → Slide 5 (Why now)
   - `brief.narrative.traction` → Slide 6 (Traction)
   - `brief.narrative.market` → Slide 7 (Market)
   - `brief.fundraising` → Slide 8 (Ask)

3. **Generate Slidev deck**:
   ```bash
   python3 $SOCIAL_ROOT/skills/repo-to-fundraising-pitchdeck/scripts/generate_slidev_pitchdeck.py \
     --brief .social/project-brief.json \
     --out slides.md \
     --repo-path .
   ```

4. **Polish** — Review the generated slides, ensure one idea per slide, add presenter notes with evidence/assumptions.

5. **Export to PDF**:
   ```bash
   slidev export slides.md --format pdf
   ```

6. **Present** the deck summary to the user. Offer to open for review or export to PPTX if needed.

---

## Step 11: Wrap Up

After all selected channels are complete, print a summary:

- **Brief**: `.social/project-brief.json` (saved / updated)
- **Instagram**: posted (Media ID + link) or skipped
- **LinkedIn**: posted (post URL) or skipped
- **Pitch Deck**: generated (`slides.md` + PDF) or skipped

Remind the user they can re-run `/go-to-market` to update the brief and publish to additional channels.
