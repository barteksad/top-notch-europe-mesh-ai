---
name: post-instagram
description: Generate and publish an Instagram post (photo or reel) for your hackathon project. Reads your project README, optionally generates media with AI, crafts a caption, and posts.
argument-hint: "[optional: specific angle or topic for the post]"
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

# Post to Instagram

Create and publish an Instagram post promoting the user's hackathon project.

## Step 1: Gather Project Context

Collect project context from the user's input, message history, or any arguments passed to this command. The context should include any combination of: project name, description, problem it solves, target audience, key features, tech stack, hackathon context, repo link, landing page.

If no project context is available at all, ask the user to describe their project. Pass whatever context is available to the Instagram content strategy skill.

## Step 2: Ask About Media

Present the user with this choice using AskUserQuestion:

**Question**: "How do you want to create the visual for your Instagram post?"
- **Option 1: Generate with AI** - "I'll create an image or video using AI based on your project"
- **Option 2: Provide my own** - "I have my own image or video file to use"

### If user chooses "Generate with AI"

Ask a follow-up question:
- **Option A: Image (photo post)** - "Generate a static image using Imagen 4 (best for feed posts)"
- **Option B: Video (reel)** - "Generate a short video using Veo 3 (best for reels, more engagement)"

Then:

1. Based on the project understanding, craft a detailed image/video generation prompt. The prompt should visually represent the project's concept in an appealing way for Instagram. Avoid text-heavy compositions.

2. For **images**, run:
```bash
GEMINI_API_KEY="$GEMINI_API_KEY" python3 ${CLAUDE_PLUGIN_ROOT}/scripts/generate_image.py \
  --prompt "<the crafted prompt>" \
  --output /tmp/instagram_post_image.png \
  --model imagen \
  --aspect-ratio 1:1
```

3. For **videos**, run:
```bash
GEMINI_API_KEY="$GEMINI_API_KEY" python3 ${CLAUDE_PLUGIN_ROOT}/scripts/generate_video.py \
  --prompt "<the crafted prompt>" \
  --output /tmp/instagram_post_video.mp4 \
  --model veo3 \
  --aspect-ratio 9:16 \
  --duration 8
```

4. Tell the user the media has been generated and where it's saved.

### If user chooses "Provide my own"

Ask the user: "Please provide the path to your image or video file."

Verify the file exists using Bash (`test -f`). If it's a video file (.mp4, .mov), it will be posted as a reel. If it's an image (.png, .jpg, .jpeg), it will be posted as a photo.

## Step 3: Craft the Caption

Based on the project understanding, write an engaging Instagram caption:
- Start with a compelling hook (first line)
- Tell the project story in 2-3 sentences
- Include a call to action
- Add 15-20 relevant hashtags (mix of high-volume, mid-volume, and niche)

Present the draft caption to the user and ask if they want to edit it or approve it.

## Step 4: Post to Instagram

Once the user approves the caption:

- For **photo posts**: Use the `post_photo` MCP tool with the image path and caption
- For **reels**: Use the `post_reel` MCP tool with the video path and caption

After posting, share the result with the user including the Media ID and Instagram link.

## Important Notes

- The `GEMINI_API_KEY` environment variable must be set for AI generation to work
- The Instagram MCP server must be running (configured in the project's `.mcp.json`)
- Local files are automatically uploaded to GitHub by the MCP server before posting
- Instagram requires a Business or Creator account connected via Facebook
- Images should be JPEG format; videos should be MP4, max 90 seconds
