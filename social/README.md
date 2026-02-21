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

### Instagram

Run `/post-instagram` to:
1. Read your project README to understand context
2. Choose: generate media with AI or provide your own
3. Generate an image (Imagen 4) or video (Veo 3) if requested
4. Craft a caption with hashtags
5. Post to Instagram

### LinkedIn

The `linkedin-cli` skill activates when you ask about LinkedIn posting. It provides:
- OAuth login and token exchange
- Publishing posts from terminal workflows
- Post history and engagement analytics
- Safe automation with dry-run and confirmation behavior

## Components

### Commands
- `/post-instagram` - Interactive workflow for creating and publishing Instagram posts

### Skills
- `instagram-content-strategy` - Caption writing, hashtags, and visual content strategy for Instagram
- `linkedin-cli` - LinkedIn CLI integration for OAuth, posting, analytics, and automation

### Server
- `server/server.py` - Instagram Graph API MCP server (auto-started by plugin)

### Scripts
- `scripts/generate_image.py` - AI image generation via Gemini API (Imagen 4)
- `scripts/generate_video.py` - AI video generation via Gemini API (Veo 3)
