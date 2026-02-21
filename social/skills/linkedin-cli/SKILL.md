---
name: linkedin-content-strategy
description: This skill should be used when the user asks to "post on LinkedIn", "create LinkedIn content", "publish to LinkedIn", "share project on LinkedIn", "promote on LinkedIn", "write a LinkedIn post", "LinkedIn marketing". Provides end-to-end LinkedIn content creation for hackathon projects, including post crafting, formatting, and publishing via the LinkedIn API.
---

# LinkedIn Content Strategy for Hackathon Projects

Create and publish LinkedIn content to promote hackathon and developer projects. This skill assumes project context has already been gathered and is available as input.

## Expected Input

This skill receives project context that may include any combination of:
- **Project name** and one-line description
- **Problem it solves** and target audience
- **Key features** and technical highlights
- **Tech stack** used
- **Hackathon context** (name, theme, prize won if any)
- **Repo link** (GitHub URL)
- **Landing page** or website URL
- **Specific angle or topic** the user wants to highlight

If any critical context is missing (no project name, no description), ask the user to fill in the gaps before proceeding. Do not attempt to read files or gather context on your own — work with what was provided.

## How to Handle the Input

### 1. Decide on Post Format

Present the user with a choice using AskUserQuestion:
- **Text post** — Professional narrative post (highest organic reach on LinkedIn)
- **Text + Image** — Post with an AI-generated or user-provided image
- **Article-style** — Longer-form post with structured sections

### 2. Generate an Image (if requested)

If the user wants an image, use the same generation scripts as Instagram but with LinkedIn-optimized settings:

```bash
GEMINI_API_KEY="$GEMINI_API_KEY" python3 ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py \
  --prompt "<crafted prompt>" \
  --output /tmp/linkedin_post_image.png \
  --model nanobanana-pro \
  --aspect-ratio 4:3
```

LinkedIn image guidelines:
- **4:3 or 16:9** aspect ratio (landscape performs best on LinkedIn)
- Professional, clean aesthetic — avoid memes or overly casual visuals
- Text in images should be minimal and legible
- Product screenshots, architecture diagrams, and data visualizations work well

### 3. Craft the LinkedIn Post

Using the provided project context, write a LinkedIn post following these best practices:

**Structure:**
- **Hook (line 1)** — Bold statement, surprising stat, or question. This is what shows before "...see more"
- **Story (3-5 short paragraphs)** — The problem, the build, and the result. Use short sentences and line breaks
- **Takeaway** — What others can learn from this
- **Call to action** — "Try it out", "Check the repo", "What do you think?"
- **Hashtags** — 3-5 max (LinkedIn penalizes hashtag spam)

**LinkedIn-specific formatting:**
- Use line breaks liberally (one idea per line)
- Keep paragraphs to 1-2 sentences
- Use unicode symbols sparingly for structure (arrows, bullets)
- No emojis in the first line (looks spammy)
- Tag relevant people/companies with @mentions if applicable
- Keep total length under 1300 characters for best engagement (under 3000 max)

**Tone:** Professional but human. First person. Avoid corporate jargon. Write like you're telling a colleague about something you built.

### 4. Select Hashtags

Use 3-5 relevant hashtags (LinkedIn's sweet spot):
- **Broad** (1-2): #hackathon #buildinpublic #startup
- **Domain** (1-2): Based on tech stack or problem area (#AI #webdev #fintech)
- **Niche** (1): Hackathon name or specific community

### 5. Present and Post

Present the draft post to the user and ask if they want to edit or approve it.

Once approved, use the LinkedIn CLI to publish:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/linkedin-cli/scripts/linkedin_cli.py post create \
  --text "<the post text>" \
  --visibility public
```

Share the result with the user including the post URL.

## Post Templates

### Launch Announcement
```
I just shipped [project name] — [one-line hook].

We built it in [timeframe] at [hackathon].

The problem: [1 sentence]
The solution: [1 sentence]
The result: [metric or outcome]

[What's next or lesson learned]

Try it out: [link]

#hackathon #buildinpublic #[domain]
```

### Technical Deep Dive
```
Here's how we built [feature] in [timeframe]:

[Problem in 1 sentence]

Our approach:
- [Technical decision 1 and why]
- [Technical decision 2 and why]
- [Unexpected challenge and how we solved it]

The takeaway: [lesson]

Code is open source: [link]

#opensource #[techstack] #[domain]
```

### Lessons Learned
```
[Number] things I learned building [project] at [hackathon]:

1. [Lesson] — [brief explanation]
2. [Lesson] — [brief explanation]
3. [Lesson] — [brief explanation]

The biggest surprise: [insight]

If you're building something similar: [advice]

[link]

#hackathon #buildinpublic #[domain]
```

## Reference Files

- `references/cli_spec.md` — LinkedIn CLI command reference
- `references/output_contracts.md` — API response schemas
- `scripts/linkedin_cli.py` — LinkedIn CLI implementation
- `assets/contracts/post_receipt.schema.json` — Post receipt schema
- `assets/contracts/post_analytics.schema.json` — Analytics schema
