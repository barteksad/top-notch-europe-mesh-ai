"""
Instagram Graph API MCP Server
Provides tools to publish photos and reels to Instagram via the official Graph API.
Supports uploading local files to GitHub before publishing.
"""

import os
import time
import uuid
import base64
import httpx
from mcp.server.fastmcp import FastMCP

# ── Configuration ────────────────────────────────────────────────────────────

GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN", "")
IG_USER_ID = os.environ.get("INSTAGRAM_USER_ID", "")

# GitHub configuration for local file uploads
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "")  # e.g. "username/repo-name"

# ── MCP Server ───────────────────────────────────────────────────────────────

mcp = FastMCP(
    "Instagram Publisher",
    instructions="Publish photos and reels to Instagram via the Graph API",
)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _check_config() -> None:
    """Raise if required env vars are missing."""
    if not ACCESS_TOKEN:
        raise ValueError(
            "INSTAGRAM_ACCESS_TOKEN environment variable is not set. "
            "Get one from https://developers.facebook.com/tools/explorer/"
        )
    if not IG_USER_ID:
        raise ValueError(
            "INSTAGRAM_USER_ID environment variable is not set. "
            "This is your Instagram Business account's Graph API user ID."
        )


def _check_github_config() -> None:
    """Raise if GitHub env vars are missing."""
    missing = []
    if not GITHUB_TOKEN:
        missing.append("GITHUB_TOKEN")
    if not GITHUB_REPO:
        missing.append("GITHUB_REPO")
    if missing:
        raise ValueError(
            f"Missing GitHub environment variables: {', '.join(missing)}. "
            "These are required for uploading local files."
        )


def _is_local_path(path: str) -> bool:
    """Check if a string looks like a local file path rather than a URL."""
    return not path.startswith(("http://", "https://")) and os.path.exists(path)


async def _upload_to_github(local_path: str) -> str:
    """Upload a local file to GitHub and return its raw public URL."""
    _check_github_config()

    if not os.path.isfile(local_path):
        raise FileNotFoundError(f"File not found: {local_path}")

    with open(local_path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode()

    ext = os.path.splitext(local_path)[1]
    file_path = f"uploads/{uuid.uuid4().hex}{ext}"

    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{file_path}"

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.put(
            url,
            headers={
                "Authorization": f"Bearer {GITHUB_TOKEN}",
                "Accept": "application/vnd.github+json",
            },
            json={
                "message": f"Upload media: {os.path.basename(local_path)}",
                "content": content_b64,
            },
        )
        resp.raise_for_status()

    public_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/main/{file_path}"
    return public_url


async def _create_container(params: dict) -> str:
    """POST to /{ig-user-id}/media to create a media container."""
    _check_config()
    url = f"{GRAPH_API_BASE}/{IG_USER_ID}/media"
    params["access_token"] = ACCESS_TOKEN

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, data=params)
        resp.raise_for_status()
        data = resp.json()

    if "id" not in data:
        raise RuntimeError(f"Container creation failed: {data}")
    return data["id"]


async def _wait_for_container(container_id: str, max_wait: int = 120) -> str:
    """Poll container status until it is FINISHED or times out."""
    url = f"{GRAPH_API_BASE}/{container_id}"
    params = {
        "fields": "status_code,status",
        "access_token": ACCESS_TOKEN,
    }
    deadline = time.time() + max_wait

    async with httpx.AsyncClient(timeout=30) as client:
        while time.time() < deadline:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status_code", "UNKNOWN")

            if status == "FINISHED":
                return status
            if status == "ERROR":
                raise RuntimeError(
                    f"Container processing failed: {data.get('status', 'unknown error')}"
                )

            # Still processing – wait before retrying
            await _async_sleep(5)

    raise TimeoutError(
        f"Container {container_id} did not finish processing within {max_wait}s"
    )


async def _async_sleep(seconds: float) -> None:
    """Async-friendly sleep."""
    import asyncio
    await asyncio.sleep(seconds)


async def _publish_container(container_id: str) -> dict:
    """POST to /{ig-user-id}/media_publish to publish the container."""
    url = f"{GRAPH_API_BASE}/{IG_USER_ID}/media_publish"
    params = {
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, data=params)
        resp.raise_for_status()
        return resp.json()


# ── Tools ────────────────────────────────────────────────────────────────────


@mcp.tool()
async def post_photo(
    image_url: str,
    caption: str = "",
    location_id: str = "",
    user_tags: str = "",
) -> str:
    """
    Publish a photo to Instagram.

    Args:
        image_url: Public URL of the image (JPEG), OR a local file path.
                   Local files are automatically uploaded to GitHub.
        caption: Optional caption text. Supports hashtags and mentions.
        location_id: Optional Facebook Page ID of the location to tag.
        user_tags: Optional JSON array of user tags. Each object needs: username, x (0.0-1.0), y (0.0-1.0).
                   Example: [{"username":"natgeo","x":0.5,"y":0.5}]
    """
    if _is_local_path(image_url):
        image_url = await _upload_to_github(image_url)

    params: dict = {
        "image_url": image_url,
    }
    if caption:
        params["caption"] = caption
    if location_id:
        params["location_id"] = location_id
    if user_tags:
        params["user_tags"] = user_tags

    # Step 1: Create container
    container_id = await _create_container(params)

    # Step 2: Publish (photos usually don't need status polling)
    result = await _publish_container(container_id)
    media_id = result.get("id", "unknown")

    return (
        f"Photo published successfully!\n"
        f"Media ID: {media_id}\n"
        f"View: https://www.instagram.com/p/{media_id}/"
    )


@mcp.tool()
async def post_reel(
    video_url: str,
    caption: str = "",
    share_to_feed: bool = True,
    thumb_offset: int = 0,
    location_id: str = "",
    cover_url: str = "",
) -> str:
    """
    Publish a reel (video) to Instagram.

    Args:
        video_url: Public URL of the video file (MP4, max 90 seconds), OR a local file path.
                   Local files are automatically uploaded to GitHub.
        caption: Optional caption text. Supports hashtags and mentions.
        share_to_feed: Whether to also show the reel in the main feed (default: True).
        thumb_offset: Thumbnail offset in milliseconds from the start of the video.
        location_id: Optional Facebook Page ID of the location to tag.
        cover_url: Optional public URL for a custom cover image, OR a local file path.
    """
    if _is_local_path(video_url):
        video_url = await _upload_to_github(video_url)
    if cover_url and _is_local_path(cover_url):
        cover_url = await _upload_to_github(cover_url)

    params: dict = {
        "media_type": "REELS",
        "video_url": video_url,
    }
    if caption:
        params["caption"] = caption
    if share_to_feed is not None:
        params["share_to_feed"] = str(share_to_feed).lower()
    if thumb_offset:
        params["thumb_offset"] = str(thumb_offset)
    if location_id:
        params["location_id"] = location_id
    if cover_url:
        params["cover_url"] = cover_url

    # Step 1: Create container
    container_id = await _create_container(params)

    # Step 2: Wait for video processing
    await _wait_for_container(container_id, max_wait=300)

    # Step 3: Publish
    result = await _publish_container(container_id)
    media_id = result.get("id", "unknown")

    return (
        f"Reel published successfully!\n"
        f"Media ID: {media_id}\n"
        f"View: https://www.instagram.com/reel/{media_id}/"
    )


# ── Entrypoint ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
