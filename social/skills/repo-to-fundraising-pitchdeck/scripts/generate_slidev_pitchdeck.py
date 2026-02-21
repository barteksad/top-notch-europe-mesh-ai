#!/usr/bin/env python3
"""Generate an 8-slide Slidev fundraising deck from a structured JSON brief."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    ".next",
    ".nuxt",
    ".vite",
    "dist",
    "build",
    ".turbo",
    ".idea",
    ".vscode",
    "__pycache__",
    "coverage",
    ".pytest_cache",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate Slidev markdown for an 8-slide fundraising deck."
    )
    parser.add_argument(
        "--brief",
        required=True,
        help="Path to the JSON brief (see references/brief-template.json).",
    )
    parser.add_argument(
        "--out",
        default="slides.md",
        help="Output Slidev markdown path. Default: slides.md",
    )
    parser.add_argument(
        "--repo-path",
        default=None,
        help="Optional repository path used to auto-generate evidence signals.",
    )
    return parser.parse_args()


def load_brief(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Brief must be a JSON object.")
    return data


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return re.sub(r"\s+", " ", text)


def normalize_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items = [clean_text(v) for v in value]
        return [v for v in items if v]
    if isinstance(value, str):
        parts = [clean_text(v) for v in re.split(r"[;\n]+", value)]
        return [v for v in parts if v]
    text = clean_text(value)
    return [text] if text else []


def yaml_str(value: str) -> str:
    return json.dumps(value)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "fundraising-deck"


def section(brief: dict[str, Any], key: str) -> dict[str, Any]:
    value = brief.get(key, {})
    return value if isinstance(value, dict) else {}


def gather_repo_signals(repo_path: Path) -> list[str]:
    if not repo_path.exists() or not repo_path.is_dir():
        return []

    file_count = 0
    extension_counts: Counter[str] = Counter()
    manifests: list[str] = []
    manifest_names = (
        "package.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "bun.lock",
        "pyproject.toml",
        "requirements.txt",
        "poetry.lock",
        "go.mod",
        "Cargo.toml",
        "pom.xml",
        "build.gradle",
        "Gemfile",
        "composer.json",
    )

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if name.startswith("."):
                continue
            file_count += 1
            lower = name.lower()
            if lower in manifest_names:
                manifests.append(name)
            ext = Path(name).suffix.lower()
            if ext:
                extension_counts[ext] += 1

    top_exts = ", ".join(
        f"{ext} ({count})" for ext, count in extension_counts.most_common(5)
    )
    top_exts = top_exts or "not enough typed files"

    signals = [
        f"Repository footprint: ~{file_count} files scanned.",
        f"Most common file extensions: {top_exts}.",
    ]

    if manifests:
        seen = sorted(set(manifests))
        signals.append(f"Build/runtime manifests detected: {', '.join(seen)}.")

    git_count = run_git(repo_path, ["rev-list", "--count", "HEAD"])
    if git_count:
        signals.append(f"Git commits in history: {git_count}.")

    git_last = run_git(repo_path, ["log", "-1", "--date=short", "--pretty=format:%cd"])
    if git_last:
        signals.append(f"Latest commit date: {git_last}.")

    return signals


def run_git(repo_path: Path, args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
    return clean_text(result.stdout)


def compose_slide_bullets(
    section_obj: dict[str, Any], fallback: list[str], max_items: int = 5
) -> list[str]:
    bullets: list[str] = []
    headline = clean_text(section_obj.get("headline"))
    if headline:
        bullets.append(f"**{headline}**")
    bullets.extend(normalize_list(section_obj.get("bullets")))
    if not bullets:
        bullets = fallback
    return bullets[:max_items]


def compose_notes(section_obj: dict[str, Any], extra_evidence: list[str] | None = None) -> str:
    evidence = normalize_list(section_obj.get("evidence"))
    assumptions = normalize_list(section_obj.get("assumptions"))

    if extra_evidence:
        evidence.extend(extra_evidence)

    lines: list[str] = []
    if evidence:
        lines.append("Evidence:")
        lines.extend([f"- {item}" for item in evidence])
    if assumptions:
        if lines:
            lines.append("")
        lines.append("Assumptions to confirm:")
        lines.extend([f"- {item}" for item in assumptions])

    if not lines:
        return ""

    note_body = "\n".join(lines)
    return f"<!--\n{note_body}\n-->"


def render_slide(
    title: str,
    bullets: list[str],
    layout: str = "default",
    notes: str = "",
    heading_level: int = 1,
) -> str:
    heading = "#" * heading_level
    out: list[str] = []
    out.append("---")
    out.append(f"layout: {layout}")
    out.append("---")
    out.append("")
    out.append(f"{heading} {title}")
    out.append("")
    out.extend([f"- {bullet}" for bullet in bullets])
    out.append("")
    if notes:
        out.append(notes)
        out.append("")
    return "\n".join(out).rstrip()


def render_deck(brief: dict[str, Any], repo_signals: list[str]) -> str:
    project = section(brief, "project")
    team = section(brief, "team")
    problem = section(brief, "problem")
    solution = section(brief, "solution")
    why_now = section(brief, "why_now")
    traction = section(brief, "traction")
    market = section(brief, "market")
    ask = section(brief, "ask")

    name = clean_text(project.get("name")) or "Project Name"
    one_liner = clean_text(project.get("one_liner")) or "One sentence product pitch."
    stage = clean_text(project.get("stage")) or "pre-seed"
    website = clean_text(project.get("website"))
    repo_url = clean_text(project.get("repo_url"))

    raise_amount = clean_text(ask.get("amount")) or clean_text(project.get("raise_amount"))
    runway = clean_text(ask.get("runway_months")) or clean_text(project.get("target_runway_months"))

    title = f"{name} | Fundraising Deck"
    export_filename = f"{slugify(name)}-fundraising-deck"

    headmatter = [
        "---",
        "theme: default",
        f"title: {yaml_str(title)}",
        "info: |",
        "  Generated with repo-to-fundraising-pitchdeck.",
        "mdc: true",
        "drawings:",
        "  enabled: false",
        f"exportFilename: {yaml_str(export_filename)}",
        "---",
        "",
    ]

    cover_bullets = [one_liner, f"Stage: {stage}"]
    if website:
        cover_bullets.append(f"Website: {website}")
    if repo_url:
        cover_bullets.append(f"Repository: {repo_url}")
    if raise_amount:
        cover_bullets.append(f"Target raise: {raise_amount}")
    cover_notes = compose_notes(project)

    traction_extra = repo_signals if repo_signals else None

    ask_bullets = compose_slide_bullets(
        ask,
        [
            "Raise amount and runway target.",
            "Milestones to hit before next round.",
            "Use-of-funds breakdown.",
        ],
    )
    if raise_amount:
        ask_bullets.insert(0, f"Raise amount: {raise_amount}")
    if runway:
        ask_bullets.insert(1 if raise_amount else 0, f"Runway target: {runway} months")

    milestones = normalize_list(ask.get("milestones"))
    if milestones:
        ask_bullets.extend([f"Milestone: {m}" for m in milestones[:2]])

    use_of_funds = normalize_list(ask.get("use_of_funds"))
    if use_of_funds:
        ask_bullets.extend([f"Use of funds: {u}" for u in use_of_funds[:2]])

    ask_bullets = ask_bullets[:6]

    slides = [
        render_slide(name, cover_bullets[:5], layout="cover", notes=cover_notes),
        render_slide(
            "Team",
            compose_slide_bullets(
                team,
                [
                    "Founders with domain expertise and execution history.",
                    "Relevant prior wins and technical credibility.",
                    "Clear ownership across product, go-to-market, and engineering.",
                ],
            ),
            notes=compose_notes(team),
        ),
        render_slide(
            "Problem",
            compose_slide_bullets(
                problem,
                [
                    "High-frequency pain for a clearly defined customer segment.",
                    "Current alternatives are slow, costly, or unreliable.",
                    "Problem causes measurable revenue, cost, or risk impact.",
                ],
            ),
            notes=compose_notes(problem),
        ),
        render_slide(
            "Solution",
            compose_slide_bullets(
                solution,
                [
                    "Product approach that removes the main bottleneck.",
                    "Differentiator that incumbents cannot easily copy.",
                    "Defensibility via product, data, workflow, or distribution.",
                ],
            ),
            notes=compose_notes(solution),
        ),
        render_slide(
            "Why Now",
            compose_slide_bullets(
                why_now,
                [
                    "A timing shift makes adoption feasible now.",
                    "Market conditions support faster distribution.",
                    "Window exists to build a category leader.",
                ],
            ),
            notes=compose_notes(why_now),
        ),
        render_slide(
            "Traction",
            compose_slide_bullets(
                traction,
                [
                    "Validation data from users, pilots, or design partners.",
                    "Evidence of execution speed and shipping cadence.",
                    "Leading indicators that support repeatable demand.",
                ],
            ),
            notes=compose_notes(traction, extra_evidence=traction_extra),
        ),
        render_slide(
            "Market",
            compose_slide_bullets(
                market,
                [
                    "Large market with a realistic beachhead.",
                    "Clear wedge-to-expansion path.",
                    "Assumptions backed by transparent sizing logic.",
                ],
            ),
            notes=compose_notes(market),
        ),
        render_slide("Ask", ask_bullets, notes=compose_notes(ask)),
    ]

    # Each slide renderer already emits slide frontmatter (`--- ... ---`), so
    # adding another separator between slides creates unintended blank pages.
    return "\n\n".join(["\n".join(headmatter).rstrip(), *slides]).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    brief_path = Path(args.brief).resolve()
    out_path = Path(args.out).resolve()
    repo_path = Path(args.repo_path).resolve() if args.repo_path else None

    brief = load_brief(brief_path)
    repo_signals = gather_repo_signals(repo_path) if repo_path else []
    output = render_deck(brief, repo_signals)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(output, encoding="utf-8")

    print(f"Generated deck: {out_path}")
    if repo_signals:
        print("Included repository signals:")
        for signal in repo_signals:
            print(f"- {signal}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
