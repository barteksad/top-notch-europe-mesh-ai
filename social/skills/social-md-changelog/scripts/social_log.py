#!/usr/bin/env python3
"""Initialize and append entries to SOCIAL.md."""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys
from typing import List, Sequence, Tuple


LEDGER_HEADER = """# SOCIAL.md

Repository social activity changelog for agent-driven actions.

## Conventions
- Keep this file append-only.
- Log each draft, publish, repurpose, analytics snapshot, and major engagement action.
- Use `social(<platform>): ...` commit subjects and link entry IDs in commit bodies.

## Entries

"""

ENTRY_HEADER_RE = re.compile(
    r"^## (SOC-(\d{8})-(\d{3})) \| ([^|]+) \| ([^|]+) \| ([^\n]+)$",
    re.MULTILINE,
)


def utc_now_iso() -> str:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    return now.isoformat().replace("+00:00", "Z")


def parse_iso_utc(raw: str) -> str:
    value = raw.strip()
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = dt.datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    parsed = parsed.astimezone(dt.timezone.utc).replace(microsecond=0)
    return parsed.isoformat().replace("+00:00", "Z")


def date_key(timestamp_iso: str) -> str:
    normalized = timestamp_iso.replace("Z", "+00:00")
    parsed = dt.datetime.fromisoformat(normalized)
    return parsed.strftime("%Y%m%d")


def dedupe(items: Sequence[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        value = item.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def parse_links(raw_links: Sequence[str]) -> List[Tuple[str, str]]:
    links: List[Tuple[str, str]] = []
    for raw in raw_links:
        item = raw.strip()
        if not item:
            continue
        if "=" in item:
            label, url = item.split("=", 1)
            links.append((label.strip(), url.strip()))
        else:
            links.append(("link", item))
    return links


def ensure_ledger(path: pathlib.Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(LEDGER_HEADER, encoding="utf-8")


def load_text(path: pathlib.Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def next_entry_id(markdown: str, date_str: str) -> str:
    pattern = re.compile(rf"^## (SOC-{date_str}-(\d{{3}})) \| ", re.MULTILINE)
    sequence = [int(match.group(2)) for match in pattern.finditer(markdown)]
    return f"SOC-{date_str}-{(max(sequence) + 1) if sequence else 1:03d}"


def extract_field(block: str, field: str) -> str:
    match = re.search(rf"^- {re.escape(field)}:\s*(.*)$", block, flags=re.MULTILINE)
    return match.group(1).strip() if match else ""


def parse_entries(markdown: str) -> List[dict]:
    matches = list(ENTRY_HEADER_RE.finditer(markdown))
    entries: List[dict] = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(markdown)
        block = markdown[start:end]
        entries.append(
            {
                "id": match.group(1),
                "timestamp": match.group(4).strip(),
                "platform": match.group(5).strip(),
                "action": match.group(6).strip(),
                "title": extract_field(block, "Title"),
                "summary": extract_field(block, "Summary"),
            }
        )
    return entries


def validate_entry_id(value: str) -> str:
    if not re.fullmatch(r"SOC-\d{8}-\d{3}", value):
        raise ValueError("entry id must match SOC-YYYYMMDD-NNN")
    return value


def render_entry(
    *,
    entry_id: str,
    timestamp: str,
    platform: str,
    action: str,
    title: str,
    status: str,
    summary: str,
    links: Sequence[Tuple[str, str]],
    assets: Sequence[str],
    commits: Sequence[str],
    tags: Sequence[str],
    content: str,
    notes: str,
) -> str:
    lines = [
        f"## {entry_id} | {timestamp} | {platform} | {action}",
        "",
        f"- Title: {title}",
        f"- Status: {status}",
        f"- Summary: {summary}",
    ]

    for label, url in links:
        lines.append(f"- Link: {label} -> {url}")
    for asset in assets:
        lines.append(f"- Asset: {asset}")
    for commit in commits:
        lines.append(f"- Commit: {commit}")
    for tag in tags:
        lines.append(f"- Tag: {tag}")

    if content:
        lines.extend(["", "### Content", "```text", content.rstrip("\n"), "```"])
    if notes:
        lines.extend(["", "### Notes", notes.strip()])

    lines.extend(["", "---", ""])
    return "\n".join(lines)


def cmd_init(args: argparse.Namespace) -> int:
    path = pathlib.Path(args.path)
    if path.exists() and not args.force:
        print(f"[skip] {path} already exists")
        return 0
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(LEDGER_HEADER, encoding="utf-8")
    print(f"[ok] initialized {path}")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    path = pathlib.Path(args.path)
    ensure_ledger(path)

    timestamp = parse_iso_utc(args.at) if args.at else utc_now_iso()
    date_str = date_key(timestamp)

    existing = load_text(path)
    entry_id = validate_entry_id(args.entry_id) if args.entry_id else next_entry_id(existing, date_str)
    if re.search(rf"^## {re.escape(entry_id)} \| ", existing, flags=re.MULTILINE):
        print(f"[error] entry id already exists: {entry_id}", file=sys.stderr)
        return 1

    content = args.content
    if args.content_file:
        content = pathlib.Path(args.content_file).read_text(encoding="utf-8")

    rendered = render_entry(
        entry_id=entry_id,
        timestamp=timestamp,
        platform=args.platform.strip().lower(),
        action=args.action.strip().lower(),
        title=args.title.strip(),
        status=args.status.strip().lower(),
        summary=args.summary.strip(),
        links=parse_links(args.link),
        assets=dedupe(args.asset),
        commits=dedupe(args.commit),
        tags=dedupe(args.tag),
        content=content,
        notes=args.notes,
    )

    if args.dry_run:
        print(rendered)
        return 0

    prefix = ""
    if existing and not existing.endswith("\n"):
        prefix = "\n\n"
    elif existing and not existing.endswith("\n\n"):
        prefix = "\n"

    path.write_text(existing + prefix + rendered, encoding="utf-8")
    print(f"[ok] added {entry_id} to {path}")
    return 0


def cmd_recent(args: argparse.Namespace) -> int:
    path = pathlib.Path(args.path)
    if not path.exists():
        print(f"[info] {path} does not exist")
        return 0

    entries = parse_entries(load_text(path))
    if not entries:
        print("[info] no entries found")
        return 0

    limit = max(1, args.limit)
    for entry in reversed(entries[-limit:]):
        print(
            f"{entry['id']} | {entry['timestamp']} | "
            f"{entry['platform']} | {entry['action']}"
        )
        if entry["title"]:
            print(f"  title: {entry['title']}")
        if entry["summary"]:
            print(f"  summary: {entry['summary']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Initialize and append entries to SOCIAL.md."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a SOCIAL.md ledger")
    init_parser.add_argument("--path", default="SOCIAL.md", help="Path to SOCIAL.md")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing file")
    init_parser.set_defaults(func=cmd_init)

    add_parser = subparsers.add_parser("add", help="Append a social changelog entry")
    add_parser.add_argument("--path", default="SOCIAL.md", help="Path to SOCIAL.md")
    add_parser.add_argument("--platform", required=True, help="Social platform")
    add_parser.add_argument("--action", required=True, help="Action type")
    add_parser.add_argument("--status", default="draft", help="Entry status")
    add_parser.add_argument("--title", required=True, help="Entry title")
    add_parser.add_argument("--summary", required=True, help="One-line outcome summary")
    add_parser.add_argument("--content", default="", help="Inline content text")
    add_parser.add_argument("--content-file", help="Path to text file with full content")
    add_parser.add_argument("--link", action="append", default=[], help="label=url or url")
    add_parser.add_argument("--asset", action="append", default=[], help="Asset path")
    add_parser.add_argument("--commit", action="append", default=[], help="Related commit hash")
    add_parser.add_argument("--tag", action="append", default=[], help="Tag value")
    add_parser.add_argument("--notes", default="", help="Additional notes")
    add_parser.add_argument("--at", help="Timestamp in ISO-8601. Defaults to now (UTC)")
    add_parser.add_argument("--entry-id", help="Explicit entry id (SOC-YYYYMMDD-NNN)")
    add_parser.add_argument("--dry-run", action="store_true", help="Print entry without writing")
    add_parser.set_defaults(func=cmd_add)

    recent_parser = subparsers.add_parser("recent", help="Print recent entry summaries")
    recent_parser.add_argument("--path", default="SOCIAL.md", help="Path to SOCIAL.md")
    recent_parser.add_argument("--limit", type=int, default=10, help="Number of entries")
    recent_parser.set_defaults(func=cmd_recent)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.func(args)
    except ValueError as exc:
        print(f"[error] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
