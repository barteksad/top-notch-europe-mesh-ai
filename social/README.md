# Social Media Plugin

Social media toolkit for hackathon projects. Generate and publish content to Instagram and LinkedIn. Understands your project from the README to craft platform-optimized content.

## Prerequisites

- **Python 3.10+** with `httpx` installed (`pip install httpx`)
- **Gemini API key** for AI image/video generation
- **Instagram Business or Creator account** connected via Facebook
- **LinkedIn account** with API access for posting

## Environment Variables

| Variable | Required For | Description |
|----------|-------------|-------------|
| `GEMINI_API_KEY` | Instagram (AI generation) | Google Gemini API key from [Google AI Studio](https://aistudio.google.com/) |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram | Long-lived token with `instagram_content_publish` permission |
| `INSTAGRAM_USER_ID` | Instagram | Instagram Business account Graph API user ID |
| `GITHUB_TOKEN` | Instagram | GitHub PAT for uploading media files |
| `GITHUB_REPO` | Instagram | Target repo in `owner/repo` format |

## Setup

1. Set your environment variables.

2. Install the plugin:
   ```bash
   claude --plugin-dir /path/to/social
   ```

The Instagram MCP server is bundled in `server/` and starts automatically.

## Usage

### Go To Market (recommended)

Run `/go-to-market` for the full pipeline:
1. Analyze your repo and extract project context
2. Ask a few questions to fill gaps
3. Save a unified brief to `.social/project-brief.json`
4. Choose channels: Instagram, LinkedIn, Pitch Deck (or all three)
5. Generate content and publish to each selected channel

The brief is created once and feeds all channels — no re-explaining your project for each platform.

### Instagram (standalone)

Run `/post-instagram` to post to Instagram only. If a project brief exists from `/go-to-market`, it uses that automatically.

### LinkedIn

The `linkedin-content-strategy` skill activates when you ask about LinkedIn posting. Reads from the project brief if available.

### Pitch Deck

The `repo-to-fundraising-pitchdeck` skill activates when you ask to create a pitch deck. Maps the project brief to an 8-slide investor framework.

## Components

### Commands
- `/go-to-market` - Full pipeline: research → brief → distribute to Instagram, LinkedIn, pitch deck
- `/post-instagram` - Standalone Instagram posting workflow

### Skills
- `instagram-content-strategy` - Caption writing, hashtags, and visual content strategy for Instagram
- `linkedin-cli` - LinkedIn CLI integration for OAuth, posting, analytics, and automation

### Server
- `server/server.py` - Instagram Graph API MCP server (auto-started by plugin)

### Scripts
- `scripts/generate_image.py` - AI image generation via Gemini API (Imagen 4)
- `scripts/generate_video.py` - AI video generation via Gemini API (Veo 3)
