#!/usr/bin/env python3
"""
Generate videos using Google Gemini API (Veo 3).
Requires GEMINI_API_KEY environment variable.

Usage:
    python generate_video.py --prompt "..." --output /path/to/output.mp4 [--model veo3] [--aspect-ratio 9:16] [--duration 8]
"""

import argparse
import json
import os
import sys
import time

import httpx

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

MODELS = {
    "veo2": "veo-2.0-generate-001",
    "veo3": "veo-3.0-generate-001",
    "veo3-fast": "veo-3.0-fast-generate-001",
    "veo3.1": "veo-3.1-generate-preview",
    "veo3.1-fast": "veo-3.1-fast-generate-preview",
}


def generate_video(
    prompt: str,
    model_id: str,
    aspect_ratio: str,
    duration_seconds: str,
    poll_interval: int = 10,
    max_wait: int = 600,
) -> bytes:
    """Generate video using Veo :predictLongRunning endpoint with polling."""
    url = f"{BASE_URL}/models/{model_id}:predictLongRunning"
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "aspectRatio": aspect_ratio,
            "durationSeconds": int(duration_seconds),
        },
    }

    with httpx.Client(timeout=max_wait + 60, follow_redirects=True) as client:
        # Step 1: Start generation
        print(f"Starting video generation with {model_id}...", file=sys.stderr)
        resp = client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            print(f"ERROR: API returned {resp.status_code}: {resp.text}", file=sys.stderr)
            sys.exit(1)

        operation = resp.json()
        operation_name = operation.get("name")
        if not operation_name:
            print(f"ERROR: No operation name returned: {operation}", file=sys.stderr)
            sys.exit(1)

        print(f"Operation started: {operation_name}", file=sys.stderr)

        # Step 2: Poll for completion
        poll_url = f"{BASE_URL}/{operation_name}"
        poll_headers = {"x-goog-api-key": GEMINI_API_KEY}
        elapsed = 0

        while elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval
            print(f"Polling... ({elapsed}s elapsed)", file=sys.stderr)

            status_resp = client.get(poll_url, headers=poll_headers)
            status_resp.raise_for_status()
            status = status_resp.json()

            if status.get("done"):
                print("Video generation complete!", file=sys.stderr)
                break
        else:
            print(f"ERROR: Video generation timed out after {max_wait}s", file=sys.stderr)
            sys.exit(1)

        # Step 3: Download the video
        samples = (
            status.get("response", {})
            .get("generateVideoResponse", {})
            .get("generatedSamples", [])
        )

        if not samples:
            print(f"ERROR: No video samples in response: {json.dumps(status)}", file=sys.stderr)
            sys.exit(1)

        video_uri = samples[0]["video"]["uri"]
        print(f"Downloading video from API...", file=sys.stderr)

        dl_resp = client.get(video_uri, headers=poll_headers)
        dl_resp.raise_for_status()
        return dl_resp.content


def main():
    parser = argparse.ArgumentParser(description="Generate videos via Google Gemini API (Veo)")
    parser.add_argument("--prompt", required=True, help="Video generation prompt")
    parser.add_argument("--output", required=True, help="Output file path (e.g. output.mp4)")
    parser.add_argument(
        "--model",
        default="veo3",
        choices=list(MODELS.keys()),
        help="Model to use (default: veo3)",
    )
    parser.add_argument(
        "--aspect-ratio",
        default="9:16",
        choices=["16:9", "9:16"],
        help="Aspect ratio (default: 9:16 for Reels)",
    )
    parser.add_argument(
        "--duration",
        default="8",
        choices=["5", "6", "7", "8"],
        help="Duration in seconds (default: 8)",
    )
    parser.add_argument(
        "--max-wait",
        type=int,
        default=600,
        help="Max wait time for generation in seconds (default: 600)",
    )
    args = parser.parse_args()

    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    model_id = MODELS[args.model]

    video_bytes = generate_video(
        prompt=args.prompt,
        model_id=model_id,
        aspect_ratio=args.aspect_ratio,
        duration_seconds=args.duration,
        max_wait=args.max_wait,
    )

    with open(args.output, "wb") as f:
        f.write(video_bytes)

    # Print result to stdout for easy capture
    print(json.dumps({"status": "success", "output": args.output, "size_bytes": len(video_bytes)}))


if __name__ == "__main__":
    main()
