#!/usr/bin/env python3
"""
Generate images using Google Gemini API (Imagen 4 or Gemini native image generation).
Requires GEMINI_API_KEY environment variable.

Usage:
    python generate_image.py --prompt "..." --output /path/to/output.png [--model imagen] [--aspect-ratio 1:1]
"""

import argparse
import base64
import json
import os
import sys

import httpx

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

MODELS = {
    "imagen": "imagen-4.0-generate-001",
    "imagen-ultra": "imagen-4.0-ultra-generate-001",
    "imagen-fast": "imagen-4.0-fast-generate-001",
    "gemini-flash": "gemini-2.5-flash-preview-04-17",
    "nanobanana-pro": "nano-banana-pro-preview",
}


def generate_with_imagen(prompt: str, model_id: str, aspect_ratio: str) -> bytes:
    """Generate image using Imagen 4 :predict endpoint."""
    url = f"{BASE_URL}/models/{model_id}:predict"
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": aspect_ratio,
            "personGeneration": "allow_adult",
        },
    }

    with httpx.Client(timeout=120) as client:
        resp = client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            print(f"ERROR: API returned {resp.status_code}: {resp.text}", file=sys.stderr)
            sys.exit(1)
        data = resp.json()

    predictions = data.get("predictions", [])
    if not predictions:
        print("ERROR: No predictions returned", file=sys.stderr)
        sys.exit(1)

    return base64.b64decode(predictions[0]["bytesBase64Encoded"])


def generate_with_gemini(prompt: str, model_id: str, aspect_ratio: str) -> bytes:
    """Generate image using Gemini native :generateContent endpoint."""
    url = f"{BASE_URL}/models/{model_id}:generateContent"
    headers = {
        "x-goog-api-key": GEMINI_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {
                "aspectRatio": aspect_ratio,
            },
        },
    }

    with httpx.Client(timeout=120) as client:
        resp = client.post(url, headers=headers, json=payload)
        if resp.status_code != 200:
            print(f"ERROR: API returned {resp.status_code}: {resp.text}", file=sys.stderr)
            sys.exit(1)
        data = resp.json()

    for candidate in data.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if "inline_data" in part:
                return base64.b64decode(part["inline_data"]["data"])
            elif "text" in part:
                print(f"Model note: {part['text']}", file=sys.stderr)

    print("ERROR: No image returned in response", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Generate images via Google Gemini API")
    parser.add_argument("--prompt", required=True, help="Image generation prompt")
    parser.add_argument("--output", required=True, help="Output file path (e.g. output.png)")
    parser.add_argument(
        "--model",
        default="imagen",
        choices=list(MODELS.keys()),
        help="Model to use (default: imagen)",
    )
    parser.add_argument(
        "--aspect-ratio",
        default="1:1",
        choices=["1:1", "3:4", "4:3", "9:16", "16:9"],
        help="Aspect ratio (default: 1:1)",
    )
    args = parser.parse_args()

    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    model_id = MODELS[args.model]
    print(f"Generating image with {args.model} ({model_id})...", file=sys.stderr)

    # Gemini-based models (including Nano Banana) use :generateContent endpoint
    # Imagen models use :predict endpoint
    gemini_models = {"gemini-flash", "nanobanana-pro"}
    if args.model in gemini_models:
        img_bytes = generate_with_gemini(args.prompt, model_id, args.aspect_ratio)
    else:
        img_bytes = generate_with_imagen(args.prompt, model_id, args.aspect_ratio)

    with open(args.output, "wb") as f:
        f.write(img_bytes)

    # Print the output path to stdout for easy capture
    print(json.dumps({"status": "success", "output": args.output, "size_bytes": len(img_bytes)}))


if __name__ == "__main__":
    main()
