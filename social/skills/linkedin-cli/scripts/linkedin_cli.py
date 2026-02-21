#!/usr/bin/env python3
"""Generic LinkedIn CLI.

Self-contained command surface for LinkedIn OAuth, posting, post retrieval,
and post analytics with stable output contracts.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import secrets
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

VERSION = "1.0.0"

EXIT_SUCCESS = 0
EXIT_GENERIC = 1
EXIT_USAGE = 2
EXIT_CONFIG = 3
EXIT_NOT_IMPLEMENTED = 4
EXIT_AUTH_REQUIRED = 5
EXIT_EXTERNAL_FAILURE = 6
EXIT_CONFIRMATION_REQUIRED = 7
EXIT_INTERRUPTED = 130

DEFAULT_SCOPES = ["openid", "profile", "email", "w_member_social"]


class CLIError(Exception):
    """Handled CLI error with mapped exit code."""

    def __init__(self, message: str, code: int = EXIT_GENERIC, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


@dataclass
class CommandResult:
    payload: Dict[str, Any]
    summary: str


@dataclass
class Context:
    profile: str
    output_mode: str
    quiet: bool
    verbose: int
    no_color: bool
    no_input: bool
    dry_run: bool
    force: bool
    enqueue: bool
    config: Dict[str, Any]
    token_store: Path
    secrets_dir: Path
    jobs_dir: Path
    ledger_path: Path


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def expand_path(path_value: str) -> Path:
    return Path(path_value).expanduser().resolve()


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in ("1", "true", "yes", "y", "on"):
        return True
    if normalized in ("0", "false", "no", "n", "off"):
        return False
    raise ValueError(f"Invalid boolean value: {value}")


def split_csv(values: Optional[List[str]]) -> List[str]:
    if not values:
        return []
    out: List[str] = []
    for value in values:
        for piece in value.split(","):
            item = piece.strip()
            if item:
                out.append(item)
    return out


def load_json_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CLIError(f"Invalid JSON config file: {path} ({exc})", EXIT_CONFIG) from exc
    if not isinstance(data, dict):
        raise CLIError(f"Config file must contain a JSON object: {path}", EXIT_CONFIG)
    return data


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def resolve_project_root() -> Path:
    return Path.cwd()


def config_defaults() -> Dict[str, Any]:
    xdg_root = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))
    return {
        "defaults": {
            "profile": "default",
            "output_mode": "human",
            "redirect_uri": "http://localhost:3000/callback",
            "scopes": list(DEFAULT_SCOPES),
        },
        "paths": {
            "project_config": str(resolve_project_root() / ".linkedin-cli" / "config.json"),
            "token_store": str(xdg_root / "linkedin-cli" / "tokens.json"),
            "secrets_dir": str(xdg_root / "linkedin-cli" / "secrets"),
            "jobs_dir": str(resolve_project_root() / ".linkedin-cli" / "jobs"),
            "ledger_path": str(resolve_project_root() / ".linkedin-cli" / "posts.jsonl"),
        },
    }


def load_effective_config(args: argparse.Namespace) -> Dict[str, Any]:
    defaults = config_defaults()
    xdg_root = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config")))

    config_files: List[Path] = [
        Path("/etc/linkedin-cli/config.json"),
        xdg_root / "linkedin-cli" / "config.json",
    ]

    project_path = Path(defaults["paths"]["project_config"])
    if args.config:
        project_path = Path(args.config)
    config_files.append(project_path)

    merged: Dict[str, Any] = defaults
    for cfg_path in config_files:
        merged = deep_merge(merged, load_json_file(cfg_path))

    env_overrides: Dict[str, Any] = {}
    env_map = {
        "defaults.profile": "LINKEDIN_CLI_PROFILE",
        "defaults.output_mode": "LINKEDIN_CLI_OUTPUT",
        "defaults.redirect_uri": "LINKEDIN_CLI_REDIRECT_URI",
        "paths.token_store": "LINKEDIN_CLI_TOKEN_STORE",
        "paths.secrets_dir": "LINKEDIN_CLI_SECRETS_DIR",
        "paths.jobs_dir": "LINKEDIN_CLI_JOBS_DIR",
        "paths.ledger_path": "LINKEDIN_CLI_LEDGER_PATH",
    }
    for dotted_key, env_name in env_map.items():
        env_value = os.environ.get(env_name)
        if env_value:
            head, leaf = dotted_key.split(".")
            env_overrides.setdefault(head, {})[leaf] = env_value

    if env_overrides:
        merged = deep_merge(merged, env_overrides)

    return merged


def flatten_plain(data: Any, prefix: str = "") -> List[str]:
    lines: List[str] = []
    if isinstance(data, dict):
        for key in sorted(data.keys()):
            next_prefix = f"{prefix}.{key}" if prefix else key
            lines.extend(flatten_plain(data[key], next_prefix))
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            next_prefix = f"{prefix}[{idx}]"
            lines.extend(flatten_plain(item, next_prefix))
    else:
        value = "" if data is None else str(data)
        lines.append(f"{prefix}={value}")
    return lines


def emit_result(ctx: Context, result: CommandResult) -> None:
    if ctx.output_mode == "json":
        print(json.dumps(result.payload, ensure_ascii=True))
        return
    if ctx.output_mode == "plain":
        print("\n".join(flatten_plain(result.payload)))
        return
    if not ctx.quiet:
        print(result.summary)
    if ctx.verbose:
        print(json.dumps(result.payload, indent=2, ensure_ascii=True))


def emit_error(output_mode: str, message: str, code: int, details: Optional[Dict[str, Any]] = None) -> None:
    if output_mode == "json":
        payload = {"status": "error", "error": {"code": code, "message": message, "details": details or {}}}
        print(json.dumps(payload, ensure_ascii=True))
    elif output_mode == "plain":
        print(f"error.code={code}")
        print(f"error.message={message}")
    print(f"Error: {message}", file=sys.stderr)


def confirmation_required(ctx: Context, reason: str) -> None:
    if ctx.force or ctx.dry_run:
        return
    if ctx.no_input or not sys.stdin.isatty():
        raise CLIError(
            f"{reason}. Confirmation required in non-interactive mode: use --force or --dry-run.",
            EXIT_CONFIRMATION_REQUIRED,
        )
    prompt = f"{reason}. Continue? [y/N]: "
    response = input(prompt).strip().lower()
    if response not in ("y", "yes"):
        raise CLIError("Operation canceled by user.", EXIT_CONFIRMATION_REQUIRED)


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def token_store_read(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"profiles": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CLIError(f"Invalid token store JSON: {path} ({exc})", EXIT_CONFIG) from exc
    if not isinstance(data, dict):
        raise CLIError(f"Token store must be a JSON object: {path}", EXIT_CONFIG)
    data.setdefault("profiles", {})
    return data


def token_store_write(path: Path, data: Dict[str, Any]) -> None:
    ensure_parent_dir(path)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def read_secret_from_input(token_file: Optional[str], from_stdin: bool) -> str:
    if token_file and from_stdin:
        raise CLIError("Use only one of --token-file or --token-stdin.", EXIT_USAGE)
    if token_file:
        path = Path(token_file)
        if not path.exists():
            raise CLIError(f"Token file not found: {token_file}", EXIT_USAGE)
        raw = path.read_text(encoding="utf-8").strip()
        if not raw:
            raise CLIError(f"Token file is empty: {token_file}", EXIT_USAGE)
        return raw
    if from_stdin:
        raw = sys.stdin.read().strip()
        if not raw:
            raise CLIError("Expected token from stdin, but got empty input.", EXIT_USAGE)
        return raw
    raise CLIError("Token input required: use --token-file or --token-stdin.", EXIT_USAGE)


def write_secret_file(path: Path, value: str) -> None:
    ensure_parent_dir(path)
    path.write_text(value + "\n", encoding="utf-8")
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        # Best effort on platforms/filesystems that ignore chmod.
        pass


def read_secret_file(path: Path) -> str:
    if not path.exists():
        raise CLIError(f"Secret file not found: {path}", EXIT_AUTH_REQUIRED)
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        raise CLIError(f"Secret file is empty: {path}", EXIT_AUTH_REQUIRED)
    return raw


def hash_secret(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def oauth_state_token() -> str:
    return secrets.token_urlsafe(24)


def iso_after_seconds(seconds: Optional[int]) -> Optional[str]:
    if not seconds:
        return None
    future = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=int(seconds))
    return future.isoformat()


def oauth_resolve_client_secret(
    *,
    env_name: str,
    secret_stdin: bool,
    secret_file: Optional[str],
    fallback_secret_path: Optional[Path],
) -> str:
    if secret_file and secret_stdin:
        raise CLIError("Use only one of --client-secret-file or --client-secret-stdin.", EXIT_USAGE)
    if secret_file:
        return read_secret_file(Path(secret_file))
    if secret_stdin:
        raw = sys.stdin.read().strip()
        if not raw:
            raise CLIError("Expected client secret from stdin, but input was empty.", EXIT_USAGE)
        return raw
    env_value = os.environ.get(env_name, "").strip()
    if env_value:
        return env_value
    if fallback_secret_path:
        return read_secret_file(fallback_secret_path)
    raise CLIError(
        f"Missing client secret. Provide --client-secret-file, --client-secret-stdin, or {env_name}.",
        EXIT_AUTH_REQUIRED,
    )


def linkedin_auth_url(client_id: str, redirect_uri: str, scopes: List[str], state: str) -> str:
    query = urllib.parse.urlencode(
        {
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
        }
    )
    return f"https://www.linkedin.com/oauth/v2/authorization?{query}"


def parse_json_maybe(body_text: str) -> Optional[Any]:
    if not body_text.strip():
        return None
    try:
        return json.loads(body_text)
    except json.JSONDecodeError:
        return None


def normalize_headers(headers: Dict[str, str]) -> Dict[str, str]:
    return {k.lower(): v for k, v in headers.items()}


def http_json_request(
    *,
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    payload: Optional[Any] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    req_data: Optional[bytes] = None
    req_headers = dict(headers or {})

    if payload is not None:
        req_data = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/json")

    req = urllib.request.Request(url, data=req_data, headers=req_headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body_text = resp.read().decode("utf-8", errors="replace")
            status = int(resp.status)
            headers_out = normalize_headers(dict(resp.headers.items()))
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode("utf-8", errors="replace")
        status = int(exc.code)
        headers_out = normalize_headers(dict(exc.headers.items()))
        return {
            "ok": False,
            "status": status,
            "headers": headers_out,
            "body_text": body_text,
            "json": parse_json_maybe(body_text),
        }
    except urllib.error.URLError as exc:
        raise CLIError(f"Network request failed: {exc.reason}", EXIT_EXTERNAL_FAILURE) from exc

    return {
        "ok": status < 400,
        "status": status,
        "headers": headers_out,
        "body_text": body_text,
        "json": parse_json_maybe(body_text),
    }


def linkedin_exchange_code(
    *,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    code: str,
) -> Dict[str, Any]:
    payload = urllib.parse.urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        }
    ).encode("utf-8")

    req = urllib.request.Request(
        "https://www.linkedin.com/oauth/v2/accessToken",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise CLIError(
            f"LinkedIn token exchange failed with HTTP {exc.code}: {error_body}",
            EXIT_EXTERNAL_FAILURE,
        ) from exc
    except urllib.error.URLError as exc:
        raise CLIError(f"LinkedIn token exchange failed: {exc.reason}", EXIT_EXTERNAL_FAILURE) from exc

    try:
        data = json.loads(body)
    except json.JSONDecodeError as exc:
        raise CLIError("LinkedIn token exchange returned invalid JSON.", EXIT_EXTERNAL_FAILURE) from exc

    if "access_token" not in data:
        raise CLIError(f"LinkedIn token exchange did not return access_token: {data}", EXIT_EXTERNAL_FAILURE)

    return data


def make_operation(ctx: Context, op: str, params: Dict[str, Any], side_effect: bool = False) -> Dict[str, Any]:
    if side_effect:
        confirmation_required(ctx, f"{op} performs external side effects")
    operation = {
        "status": "ok",
        "operation": op,
        "profile": ctx.profile,
        "dry_run": ctx.dry_run,
        "params": params,
        "timestamp": utc_now(),
    }
    if ctx.enqueue:
        ensure_parent_dir(ctx.jobs_dir / "dummy")
        digest = hash_secret(json.dumps(operation, sort_keys=True, ensure_ascii=True))
        job_id = f"{dt.datetime.now().strftime('%Y%m%dT%H%M%S')}-{digest[:10]}"
        job_path = ctx.jobs_dir / f"{job_id}.json"
        job_path.write_text(json.dumps(operation, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        operation["job"] = {"id": job_id, "path": str(job_path)}
    return operation


def append_json_line(path: Path, payload: Dict[str, Any]) -> None:
    ensure_parent_dir(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def read_json_lines(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    entries: List[Dict[str, Any]] = []
    for idx, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        raw = line.strip()
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise CLIError(f"Invalid JSON line in ledger at line {idx}: {exc}", EXIT_CONFIG) from exc
        if isinstance(parsed, dict):
            entries.append(parsed)
    return entries


def derive_linkedin_post_url(post_urn: Optional[str]) -> Optional[str]:
    if not post_urn:
        return None
    if post_urn.startswith("urn:li:share:") or post_urn.startswith("urn:li:ugcPost:"):
        return f"https://www.linkedin.com/feed/update/{post_urn}/"
    return None


def linkedin_api_headers(access_token: str, json_content: bool = False) -> Dict[str, str]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    if json_content:
        headers["Content-Type"] = "application/json"
    return headers


def get_profile_state(store: Dict[str, Any], profile: str) -> Dict[str, Any]:
    profiles = store.setdefault("profiles", {})
    return profiles.setdefault(profile, {})


def get_linkedin_state(store: Dict[str, Any], profile: str) -> Dict[str, Any]:
    profile_state = get_profile_state(store, profile)
    return profile_state.setdefault("linkedin", {})


def load_access_token(ctx: Context, linkedin_state: Dict[str, Any]) -> str:
    token_file = linkedin_state.get("token_file")
    if token_file:
        return read_secret_file(Path(token_file))
    fallback = ctx.secrets_dir / ctx.profile / "linkedin.access_token"
    return read_secret_file(fallback)


def resolve_author_urn(args_author_urn: Optional[str], linkedin_state: Dict[str, Any]) -> str:
    candidate = (args_author_urn or linkedin_state.get("author_urn") or "").strip()
    if not candidate:
        raise CLIError(
            "Author URN required. Use --author-urn or run auth whoami --save-author.",
            EXIT_USAGE,
        )
    if not candidate.startswith("urn:li:person:") and not candidate.startswith("urn:li:organization:"):
        raise CLIError("Author URN must start with urn:li:person: or urn:li:organization:.", EXIT_USAGE)
    return candidate


def linkedin_profile_lookup(access_token: str) -> Dict[str, Any]:
    userinfo = http_json_request(
        method="GET",
        url="https://api.linkedin.com/v2/userinfo",
        headers=linkedin_api_headers(access_token),
    )
    if userinfo["ok"] and isinstance(userinfo["json"], dict):
        profile = userinfo["json"]
        person_id = str(profile.get("sub", "")).strip()
        author_urn = f"urn:li:person:{person_id}" if person_id else None
        return {
            "source": "userinfo",
            "author_urn": author_urn,
            "profile": profile,
            "http_status": userinfo["status"],
            "headers": userinfo["headers"],
        }

    me = http_json_request(
        method="GET",
        url="https://api.linkedin.com/v2/me",
        headers=linkedin_api_headers(access_token),
    )
    if me["ok"] and isinstance(me["json"], dict):
        profile = me["json"]
        person_id = str(profile.get("id", "")).strip()
        author_urn = f"urn:li:person:{person_id}" if person_id else None
        return {
            "source": "me",
            "author_urn": author_urn,
            "profile": profile,
            "http_status": me["status"],
            "headers": me["headers"],
        }

    raise CLIError(
        "Unable to fetch LinkedIn profile from /v2/userinfo or /v2/me. Check scopes/token validity.",
        EXIT_EXTERNAL_FAILURE,
        details={"userinfo_status": userinfo["status"], "me_status": me["status"]},
    )


def load_post_text(text: Optional[str], text_file: Optional[str], from_stdin: bool) -> str:
    provided = [bool(text), bool(text_file), bool(from_stdin)]
    if sum(provided) != 1:
        raise CLIError("Provide exactly one of --text, --text-file, or --stdin.", EXIT_USAGE)
    if text:
        return text
    if text_file:
        path = Path(text_file)
        if not path.exists():
            raise CLIError(f"Text file not found: {text_file}", EXIT_USAGE)
        body = path.read_text(encoding="utf-8").strip()
        if not body:
            raise CLIError(f"Text file is empty: {text_file}", EXIT_USAGE)
        return body
    body = sys.stdin.read().strip()
    if not body:
        raise CLIError("Expected post text from stdin, but input was empty.", EXIT_USAGE)
    return body


def build_ugc_post_payload(
    *,
    author_urn: str,
    text: str,
    visibility: str,
    link: Optional[str],
    title: Optional[str],
    description: Optional[str],
) -> Dict[str, Any]:
    share_content: Dict[str, Any] = {
        "shareCommentary": {"text": text},
        "shareMediaCategory": "NONE",
    }

    if link:
        media: Dict[str, Any] = {
            "status": "READY",
            "originalUrl": link,
            "title": {"text": title or "Link"},
        }
        if description:
            media["description"] = {"text": description}
        share_content["shareMediaCategory"] = "ARTICLE"
        share_content["media"] = [media]

    return {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": share_content,
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": visibility,
        },
    }


def cmd_init(ctx: Context, args: argparse.Namespace) -> CommandResult:
    project_root = expand_path(args.project_dir)
    config_path = project_root / ".linkedin-cli" / "config.json"
    jobs_dir = project_root / ".linkedin-cli" / "jobs"
    ledger_path = project_root / ".linkedin-cli" / "posts.jsonl"

    payload = {
        "project_root": str(project_root),
        "config_path": str(config_path),
        "jobs_dir": str(jobs_dir),
        "ledger_path": str(ledger_path),
        "token_store": str(ctx.token_store),
        "secrets_dir": str(ctx.secrets_dir),
    }

    if ctx.dry_run:
        payload["status"] = "planned"
        return CommandResult(payload=payload, summary=f"Planned project init at {project_root}")

    if config_path.exists() and not args.force:
        raise CLIError(f"Config already exists: {config_path}. Use --force to overwrite.", EXIT_CONFIRMATION_REQUIRED)

    ensure_parent_dir(config_path)
    jobs_dir.mkdir(parents=True, exist_ok=True)
    ensure_parent_dir(ledger_path)
    if not ledger_path.exists():
        ledger_path.write_text("", encoding="utf-8")

    base_config = {
        "defaults": {
            "profile": ctx.profile,
            "output_mode": "human",
            "redirect_uri": "http://localhost:3000/callback",
            "scopes": list(DEFAULT_SCOPES),
        }
    }
    config_path.write_text(json.dumps(base_config, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

    payload["status"] = "initialized"
    return CommandResult(payload=payload, summary=f"Initialized LinkedIn CLI config at {config_path}")


def cmd_auth_connect(ctx: Context, args: argparse.Namespace) -> CommandResult:
    store = token_store_read(ctx.token_store)
    linkedin_state = get_linkedin_state(store, ctx.profile)

    requested_scopes = split_csv(args.scopes) or ctx.config["defaults"].get("scopes", list(DEFAULT_SCOPES))
    redirect_uri = args.redirect_uri or ctx.config["defaults"].get("redirect_uri", "http://localhost:3000/callback")

    linkedin_state.update(
        {
            "platform": "linkedin",
            "status": linkedin_state.get("status", "pending"),
            "scopes": requested_scopes,
            "redirect_uri": redirect_uri,
            "author_urn": args.author_urn or linkedin_state.get("author_urn"),
            "updated_at": utc_now(),
        }
    )

    token_saved = False
    if args.token_file or args.token_stdin:
        secret = read_secret_from_input(args.token_file, args.token_stdin)
        secret_path = ctx.secrets_dir / ctx.profile / "linkedin.access_token"
        if not ctx.dry_run:
            write_secret_file(secret_path, secret)
        linkedin_state["status"] = "connected"
        linkedin_state["token_file"] = str(secret_path)
        linkedin_state["token_sha256"] = hash_secret(secret)
        token_saved = True

    if not ctx.dry_run:
        token_store_write(ctx.token_store, store)

    payload = {
        "status": "ok",
        "profile": ctx.profile,
        "platform": "linkedin",
        "connection_status": linkedin_state["status"],
        "scopes": requested_scopes,
        "redirect_uri": redirect_uri,
        "author_urn": linkedin_state.get("author_urn"),
        "token_saved": token_saved,
        "token_store": str(ctx.token_store),
    }
    summary = f"LinkedIn auth configured for profile '{ctx.profile}' ({linkedin_state['status']})."
    return CommandResult(payload=payload, summary=summary)


def cmd_auth_import_token(ctx: Context, args: argparse.Namespace) -> CommandResult:
    secret = read_secret_from_input(args.token_file, args.token_stdin)
    store = token_store_read(ctx.token_store)
    linkedin_state = get_linkedin_state(store, ctx.profile)

    secret_name = f"linkedin.{args.token_type}"
    secret_path = ctx.secrets_dir / ctx.profile / secret_name
    if not ctx.dry_run:
        write_secret_file(secret_path, secret)

    linkedin_state.update(
        {
            "platform": "linkedin",
            "status": "connected" if args.token_type == "access_token" else linkedin_state.get("status", "pending"),
            "updated_at": utc_now(),
        }
    )
    linkedin_state[f"{args.token_type}_file"] = str(secret_path)
    linkedin_state[f"{args.token_type}_sha256"] = hash_secret(secret)

    if args.token_type == "access_token":
        linkedin_state["token_file"] = str(secret_path)
        linkedin_state["token_sha256"] = hash_secret(secret)

    if not ctx.dry_run:
        token_store_write(ctx.token_store, store)

    payload = {
        "status": "ok",
        "profile": ctx.profile,
        "platform": "linkedin",
        "token_type": args.token_type,
        "token_file": str(secret_path),
    }
    return CommandResult(payload=payload, summary=f"Imported {args.token_type} for LinkedIn.")


def cmd_auth_status(ctx: Context, _args: argparse.Namespace) -> CommandResult:
    store = token_store_read(ctx.token_store)
    linkedin_state = get_profile_state(store, ctx.profile).get("linkedin", {"status": "not_configured"})
    payload = {"status": "ok", "profile": ctx.profile, "platform": "linkedin", "auth": linkedin_state}
    return CommandResult(payload=payload, summary=f"linkedin: {linkedin_state.get('status', 'not_configured')}")


def cmd_auth_revoke(ctx: Context, _args: argparse.Namespace) -> CommandResult:
    confirmation_required(ctx, "Revoking local auth state for linkedin")
    store = token_store_read(ctx.token_store)
    profile_state = get_profile_state(store, ctx.profile)
    linkedin_state = profile_state.pop("linkedin", None)

    deleted_files: List[str] = []
    for suffix in ("access_token", "refresh_token", "client_secret"):
        candidate = ctx.secrets_dir / ctx.profile / f"linkedin.{suffix}"
        if candidate.exists() and not ctx.dry_run:
            candidate.unlink()
            deleted_files.append(str(candidate))

    if not ctx.dry_run:
        token_store_write(ctx.token_store, store)

    payload = {
        "status": "ok",
        "profile": ctx.profile,
        "platform": "linkedin",
        "revoked": linkedin_state is not None,
        "deleted_secret_files": deleted_files,
    }
    return CommandResult(payload=payload, summary="Revoked local LinkedIn auth state.")


def cmd_auth_login(ctx: Context, args: argparse.Namespace) -> CommandResult:
    store = token_store_read(ctx.token_store)
    linkedin_state = get_linkedin_state(store, ctx.profile)

    client_id = (args.client_id or os.environ.get("LINKEDIN_CLIENT_ID", "") or linkedin_state.get("client_id", "")).strip()
    if not client_id:
        raise CLIError("Missing LinkedIn client ID. Use --client-id or LINKEDIN_CLIENT_ID.", EXIT_AUTH_REQUIRED)

    redirect_uri = (
        args.redirect_uri
        or linkedin_state.get("redirect_uri")
        or os.environ.get("LINKEDIN_CLI_REDIRECT_URI")
        or ctx.config["defaults"].get("redirect_uri")
        or "http://localhost:3000/callback"
    )
    scopes = split_csv(args.scopes) or linkedin_state.get("scopes") or ctx.config["defaults"].get("scopes", list(DEFAULT_SCOPES))
    state = args.state or oauth_state_token()

    secret_path = ctx.secrets_dir / ctx.profile / "linkedin.client_secret"
    client_secret = oauth_resolve_client_secret(
        env_name="LINKEDIN_CLIENT_SECRET",
        secret_stdin=args.client_secret_stdin,
        secret_file=args.client_secret_file,
        fallback_secret_path=secret_path if secret_path.exists() else None,
    )

    auth_url = linkedin_auth_url(client_id, redirect_uri, scopes, state)

    linkedin_state.update(
        {
            "platform": "linkedin",
            "status": "pending",
            "oauth_state": state,
            "scopes": scopes,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret_file": str(secret_path),
            "auth_url": auth_url,
            "updated_at": utc_now(),
        }
    )

    if not ctx.dry_run:
        write_secret_file(secret_path, client_secret)
        token_store_write(ctx.token_store, store)

    payload = {
        "status": "ok",
        "profile": ctx.profile,
        "platform": "linkedin",
        "redirect_uri": redirect_uri,
        "scopes": scopes,
        "state": state,
        "auth_url": auth_url,
        "next_step": "Open auth_url, approve access, then run auth exchange-code --code <CODE>.",
    }
    return CommandResult(payload=payload, summary="LinkedIn auth URL prepared.")


def cmd_auth_exchange_code(ctx: Context, args: argparse.Namespace) -> CommandResult:
    store = token_store_read(ctx.token_store)
    linkedin_state = get_linkedin_state(store, ctx.profile)

    code = args.code.strip()
    if not code:
        raise CLIError("OAuth code is required.", EXIT_USAGE)

    client_id = (args.client_id or linkedin_state.get("client_id") or os.environ.get("LINKEDIN_CLIENT_ID", "")).strip()
    if not client_id:
        raise CLIError("Missing LinkedIn client ID. Use --client-id or LINKEDIN_CLIENT_ID.", EXIT_AUTH_REQUIRED)

    redirect_uri = (
        args.redirect_uri
        or linkedin_state.get("redirect_uri")
        or os.environ.get("LINKEDIN_CLI_REDIRECT_URI")
        or ctx.config["defaults"].get("redirect_uri")
        or "http://localhost:3000/callback"
    )

    default_secret_path = ctx.secrets_dir / ctx.profile / "linkedin.client_secret"
    fallback_secret_path = Path(linkedin_state.get("client_secret_file", default_secret_path))
    client_secret = oauth_resolve_client_secret(
        env_name="LINKEDIN_CLIENT_SECRET",
        secret_stdin=args.client_secret_stdin,
        secret_file=args.client_secret_file,
        fallback_secret_path=fallback_secret_path if fallback_secret_path.exists() else None,
    )

    tokens = linkedin_exchange_code(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        code=code,
    )

    access_token = tokens["access_token"]
    refresh_token = tokens.get("refresh_token")
    access_path = ctx.secrets_dir / ctx.profile / "linkedin.access_token"
    refresh_path = ctx.secrets_dir / ctx.profile / "linkedin.refresh_token"

    if not ctx.dry_run:
        write_secret_file(access_path, access_token)
        if refresh_token:
            write_secret_file(refresh_path, refresh_token)

    linkedin_state.update(
        {
            "platform": "linkedin",
            "status": "connected",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "scopes": split_csv([tokens.get("scope", "")]) or linkedin_state.get("scopes", list(DEFAULT_SCOPES)),
            "token_file": str(access_path),
            "token_sha256": hash_secret(access_token),
            "expires_in": tokens.get("expires_in"),
            "expires_at": iso_after_seconds(tokens.get("expires_in")),
            "refresh_token_file": str(refresh_path) if refresh_token else linkedin_state.get("refresh_token_file"),
            "refresh_token_sha256": hash_secret(refresh_token) if refresh_token else linkedin_state.get("refresh_token_sha256"),
            "refresh_token_expires_in": tokens.get("refresh_token_expires_in"),
            "refresh_token_expires_at": iso_after_seconds(tokens.get("refresh_token_expires_in")),
            "updated_at": utc_now(),
        }
    )

    if not ctx.dry_run:
        token_store_write(ctx.token_store, store)

    payload = {
        "status": "ok",
        "profile": ctx.profile,
        "platform": "linkedin",
        "connected": True,
        "access_token_file": str(access_path),
        "expires_in": tokens.get("expires_in"),
        "expires_at": iso_after_seconds(tokens.get("expires_in")),
        "refresh_token_present": bool(refresh_token),
        "refresh_token_expires_in": tokens.get("refresh_token_expires_in"),
        "refresh_token_expires_at": iso_after_seconds(tokens.get("refresh_token_expires_in")),
    }
    return CommandResult(payload=payload, summary="LinkedIn access token stored and auth state connected.")


def cmd_auth_whoami(ctx: Context, args: argparse.Namespace) -> CommandResult:
    store = token_store_read(ctx.token_store)
    linkedin_state = get_linkedin_state(store, ctx.profile)

    access_token = load_access_token(ctx, linkedin_state)
    profile_info = linkedin_profile_lookup(access_token)

    if args.save_author and profile_info.get("author_urn"):
        linkedin_state["author_urn"] = profile_info["author_urn"]
        linkedin_state["updated_at"] = utc_now()
        if not ctx.dry_run:
            token_store_write(ctx.token_store, store)

    payload = {
        "status": "ok",
        "profile": ctx.profile,
        "platform": "linkedin",
        "source": profile_info["source"],
        "author_urn": profile_info.get("author_urn"),
        "saved": bool(args.save_author and profile_info.get("author_urn")),
        "profile_data": profile_info.get("profile"),
        "http_status": profile_info.get("http_status"),
    }
    return CommandResult(payload=payload, summary="Fetched LinkedIn profile details.")


def cmd_post_create(ctx: Context, args: argparse.Namespace) -> CommandResult:
    text = load_post_text(args.text, args.text_file, args.stdin)
    store = token_store_read(ctx.token_store)
    linkedin_state = get_linkedin_state(store, ctx.profile)

    author_urn = resolve_author_urn(args.author_urn, linkedin_state)
    payload_body = build_ugc_post_payload(
        author_urn=author_urn,
        text=text,
        visibility=args.visibility,
        link=args.link,
        title=args.title,
        description=args.description,
    )

    params = {
        "author_urn": author_urn,
        "visibility": args.visibility,
        "text": text,
        "link": args.link,
        "title": args.title,
        "description": args.description,
        "schedule_at": args.schedule_at,
    }
    op = make_operation(ctx, "post.create", params, side_effect=True)
    op["request"] = payload_body

    if ctx.dry_run:
        return CommandResult(payload=op, summary="Planned LinkedIn post create operation.")

    access_token = load_access_token(ctx, linkedin_state)
    response = http_json_request(
        method="POST",
        url="https://api.linkedin.com/v2/ugcPosts",
        headers=linkedin_api_headers(access_token, json_content=True),
        payload=payload_body,
    )
    if not response["ok"]:
        raise CLIError(
            f"LinkedIn post create failed with HTTP {response['status']}: {response['body_text']}",
            EXIT_EXTERNAL_FAILURE,
            details={"http_status": response["status"]},
        )

    response_headers = response["headers"]
    response_json = response["json"]
    restli_id = response_headers.get("x-restli-id")
    request_id = response_headers.get("x-linkedin-request-id")

    post_urn: Optional[str] = None
    if restli_id:
        post_urn = restli_id
    elif isinstance(response_json, dict):
        post_urn = str(response_json.get("id", "")).strip() or None

    receipt = {
        "post_urn": post_urn,
        "post_url": derive_linkedin_post_url(post_urn),
        "author_urn": author_urn,
        "visibility": args.visibility,
        "lifecycle_state": "PUBLISHED",
        "request_id": request_id,
        "restli_id": restli_id,
        "http_status": response["status"],
        "api_response": response_json,
        "response_headers": {
            "x-restli-id": response_headers.get("x-restli-id", ""),
            "x-linkedin-request-id": response_headers.get("x-linkedin-request-id", ""),
            "location": response_headers.get("location", ""),
        },
        "created_at": utc_now(),
    }

    event_hash = hash_secret(json.dumps(receipt, sort_keys=True, ensure_ascii=True))[:12]
    event_id = f"post-{dt.datetime.now().strftime('%Y%m%dT%H%M%S')}-{event_hash}"
    ledger_entry = {
        "event_id": event_id,
        "operation": "post.create",
        "profile": ctx.profile,
        "timestamp": utc_now(),
        "request": payload_body,
        "receipt": receipt,
    }
    append_json_line(ctx.ledger_path, ledger_entry)

    op["receipt"] = receipt
    op["ledger"] = {"event_id": event_id, "path": str(ctx.ledger_path)}
    return CommandResult(payload=op, summary=f"Created LinkedIn post ({post_urn or 'URN unavailable'}).")


def cmd_post_get(ctx: Context, args: argparse.Namespace) -> CommandResult:
    post_urn = args.post_urn.strip()
    if not post_urn:
        raise CLIError("--post-urn is required.", EXIT_USAGE)

    entries = read_json_lines(ctx.ledger_path)
    history_matches = [entry for entry in entries if entry.get("receipt", {}).get("post_urn") == post_urn]

    remote_payload: Optional[Dict[str, Any]] = None
    if args.source in ("remote", "both"):
        store = token_store_read(ctx.token_store)
        linkedin_state = get_linkedin_state(store, ctx.profile)
        access_token = load_access_token(ctx, linkedin_state)

        encoded = urllib.parse.quote(post_urn, safe="")
        response = http_json_request(
            method="GET",
            url=f"https://api.linkedin.com/v2/ugcPosts/{encoded}",
            headers=linkedin_api_headers(access_token),
        )
        if not response["ok"]:
            raise CLIError(
                f"LinkedIn post get failed with HTTP {response['status']}: {response['body_text']}",
                EXIT_EXTERNAL_FAILURE,
                details={"http_status": response["status"]},
            )
        remote_payload = {
            "http_status": response["status"],
            "headers": response["headers"],
            "body": response["json"] if response["json"] is not None else response["body_text"],
        }

    payload = {
        "status": "ok",
        "operation": "post.get",
        "profile": ctx.profile,
        "post_urn": post_urn,
        "remote": remote_payload if args.source in ("remote", "both") else None,
        "history": history_matches if args.source in ("ledger", "both") else [],
    }
    return CommandResult(payload=payload, summary=f"Fetched LinkedIn post details for {post_urn}.")


def cmd_post_list(ctx: Context, args: argparse.Namespace) -> CommandResult:
    remote_payload: Optional[Dict[str, Any]] = None
    author_urn: Optional[str] = args.author_urn

    if args.source in ("remote", "both"):
        store = token_store_read(ctx.token_store)
        linkedin_state = get_linkedin_state(store, ctx.profile)
        author_urn = resolve_author_urn(args.author_urn, linkedin_state)
        access_token = load_access_token(ctx, linkedin_state)

        query = urllib.parse.urlencode(
            {
                "q": "authors",
                "authors": f"List({author_urn})",
                "sortBy": "LAST_MODIFIED",
                "count": args.count,
                "start": args.start,
            }
        )
        response = http_json_request(
            method="GET",
            url=f"https://api.linkedin.com/v2/ugcPosts?{query}",
            headers=linkedin_api_headers(access_token),
        )
        if not response["ok"]:
            raise CLIError(
                f"LinkedIn post list failed with HTTP {response['status']}: {response['body_text']}",
                EXIT_EXTERNAL_FAILURE,
                details={"http_status": response["status"]},
            )
        remote_payload = {
            "http_status": response["status"],
            "headers": response["headers"],
            "body": response["json"] if response["json"] is not None else response["body_text"],
        }

    entries = read_json_lines(ctx.ledger_path)
    history = entries
    if author_urn:
        history = [entry for entry in history if entry.get("receipt", {}).get("author_urn") == author_urn]
    if args.limit and args.limit > 0:
        history = history[-args.limit :]

    payload = {
        "status": "ok",
        "operation": "post.list",
        "profile": ctx.profile,
        "author_urn": author_urn,
        "remote": remote_payload if args.source in ("remote", "both") else None,
        "history": history if args.source in ("ledger", "both") else [],
    }
    return CommandResult(payload=payload, summary="Fetched LinkedIn post list.")


def cmd_post_history(ctx: Context, args: argparse.Namespace) -> CommandResult:
    entries = read_json_lines(ctx.ledger_path)

    if args.post_urn:
        entries = [entry for entry in entries if entry.get("receipt", {}).get("post_urn") == args.post_urn]
    if args.author_urn:
        entries = [entry for entry in entries if entry.get("receipt", {}).get("author_urn") == args.author_urn]
    if args.contains:
        needle = args.contains.lower()
        entries = [entry for entry in entries if needle in json.dumps(entry, ensure_ascii=True).lower()]

    if args.limit and args.limit > 0:
        entries = entries[-args.limit :]

    payload = {
        "status": "ok",
        "operation": "post.history",
        "profile": ctx.profile,
        "count": len(entries),
        "entries": entries,
    }
    return CommandResult(payload=payload, summary=f"Loaded {len(entries)} local post receipt event(s).")


def cmd_analytics_get(ctx: Context, args: argparse.Namespace) -> CommandResult:
    post_urn = args.post_urn.strip()
    if not post_urn:
        raise CLIError("--post-urn is required.", EXIT_USAGE)

    store = token_store_read(ctx.token_store)
    linkedin_state = get_linkedin_state(store, ctx.profile)
    access_token = load_access_token(ctx, linkedin_state)

    encoded = urllib.parse.quote(post_urn, safe="")
    response = http_json_request(
        method="GET",
        url=f"https://api.linkedin.com/v2/socialActions/{encoded}",
        headers=linkedin_api_headers(access_token),
    )
    if not response["ok"]:
        raise CLIError(
            f"LinkedIn analytics get failed with HTTP {response['status']}: {response['body_text']}",
            EXIT_EXTERNAL_FAILURE,
            details={"http_status": response["status"]},
        )

    body = response["json"] if isinstance(response["json"], dict) else {}
    likes = int(body.get("likesSummary", {}).get("totalLikes", 0) or 0)

    comments_summary = body.get("commentsSummary", {})
    comments = int(
        comments_summary.get("totalFirstLevelComments", comments_summary.get("totalComments", 0)) or 0
    )

    shares_raw = body.get("sharesSummary", {}).get("totalShares")
    reactions_raw = body.get("reactionsSummary", {}).get("totalReactions")

    payload = {
        "status": "ok",
        "operation": "analytics.get",
        "profile": ctx.profile,
        "post_urn": post_urn,
        "collected_at": utc_now(),
        "engagement": {
            "likes": likes,
            "comments": comments,
            "shares": int(shares_raw) if isinstance(shares_raw, int) else None,
            "reactions": int(reactions_raw) if isinstance(reactions_raw, int) else None,
        },
        "raw": body if body else response["body_text"],
    }
    return CommandResult(payload=payload, summary=f"Fetched analytics for {post_urn}.")


def cmd_completion(_ctx: Context, args: argparse.Namespace) -> CommandResult:
    commands = "init auth post analytics completion"
    if args.shell == "bash":
        script = f"complete -W \"{commands}\" linkedin-cli"
    elif args.shell == "zsh":
        script = f"compctl -k \"{commands}\" linkedin-cli"
    else:
        script = (
            "function __fish_linkedin_cli\n"
            f"  for cmd in {commands}; echo $cmd; end\n"
            "end\n"
            "complete -c linkedin-cli -f -a '(__fish_linkedin_cli)'"
        )
    payload = {"status": "ok", "shell": args.shell, "script": script}
    return CommandResult(payload=payload, summary=script)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="linkedin-cli",
        description="LinkedIn CLI: OAuth, posting, post retrieval, and analytics.",
    )
    parser.add_argument("--version", action="version", version=f"linkedin-cli {VERSION}")
    parser.add_argument("--config", help="Path to project config JSON (overrides default project config path).")
    parser.add_argument("--profile", help="Profile name (default from config/env: 'default').")
    parser.add_argument("-q", "--quiet", action="store_true", help="Reduce non-essential output.")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase detail level (repeatable).")

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="Emit machine-readable JSON to stdout.")
    output_group.add_argument("--plain", action="store_true", help="Emit stable key=value lines to stdout.")

    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color output.")
    parser.add_argument("--no-input", action="store_true", help="Disable interactive prompts.")
    parser.add_argument("-n", "--dry-run", action="store_true", help="Plan actions without external side effects.")
    parser.add_argument("-f", "--force", action="store_true", help="Skip confirmation prompts for side effects.")
    parser.add_argument("--enqueue", action="store_true", help="Write operation envelopes to .linkedin-cli/jobs.")

    subcommands = parser.add_subparsers(dest="command", required=True)

    p_init = subcommands.add_parser("init", help="Initialize local LinkedIn CLI project config.")
    p_init.add_argument("--project-dir", default=".", help="Project root to initialize.")
    p_init.add_argument("-f", "--force", action="store_true", help="Overwrite existing config.")
    p_init.set_defaults(func=cmd_init)

    p_auth = subcommands.add_parser("auth", help="Manage LinkedIn auth configuration and token references.")
    auth_sub = p_auth.add_subparsers(dest="auth_command", required=True)

    p_auth_connect = auth_sub.add_parser("connect", help="Configure LinkedIn auth metadata.")
    p_auth_connect.add_argument("--scopes", nargs="*", help="OAuth scopes (space/comma separated).")
    p_auth_connect.add_argument("--redirect-uri", help="OAuth redirect URI.")
    p_auth_connect.add_argument("--author-urn", help="Optional default author URN.")
    p_auth_connect.add_argument("--token-file", help="Read access token from file.")
    p_auth_connect.add_argument("--token-stdin", action="store_true", help="Read access token from stdin.")
    p_auth_connect.set_defaults(func=cmd_auth_connect)

    p_auth_import = auth_sub.add_parser("import-token", help="Import token/secret from file or stdin.")
    p_auth_import.add_argument(
        "--token-type",
        choices=("access_token", "refresh_token", "client_secret"),
        default="access_token",
        help="Stored token type label.",
    )
    p_auth_import.add_argument("--token-file", help="Read token from file.")
    p_auth_import.add_argument("--token-stdin", action="store_true", help="Read token from stdin.")
    p_auth_import.set_defaults(func=cmd_auth_import_token)

    p_auth_login = auth_sub.add_parser("login", help="Start OAuth flow and print authorization URL.")
    p_auth_login.add_argument("--client-id", help="OAuth client ID (or env LINKEDIN_CLIENT_ID).")
    p_auth_login.add_argument("--client-secret-file", help="Read OAuth client secret from file.")
    p_auth_login.add_argument("--client-secret-stdin", action="store_true", help="Read OAuth client secret from stdin.")
    p_auth_login.add_argument("--redirect-uri", help="OAuth redirect URI; must match LinkedIn app settings.")
    p_auth_login.add_argument("--scopes", nargs="*", help="OAuth scopes (comma/space separated).")
    p_auth_login.add_argument("--state", help="OAuth state value (auto-generated if omitted).")
    p_auth_login.set_defaults(func=cmd_auth_login)

    p_auth_exchange = auth_sub.add_parser("exchange-code", help="Exchange OAuth callback code for tokens.")
    p_auth_exchange.add_argument("--code", required=True, help="Authorization code from LinkedIn callback.")
    p_auth_exchange.add_argument("--client-id", help="OAuth client ID (or env LINKEDIN_CLIENT_ID).")
    p_auth_exchange.add_argument("--client-secret-file", help="Read OAuth client secret from file.")
    p_auth_exchange.add_argument("--client-secret-stdin", action="store_true", help="Read OAuth client secret from stdin.")
    p_auth_exchange.add_argument("--redirect-uri", help="OAuth redirect URI used during authorization.")
    p_auth_exchange.set_defaults(func=cmd_auth_exchange_code)

    p_auth_whoami = auth_sub.add_parser("whoami", help="Fetch authenticated LinkedIn profile details.")
    p_auth_whoami.add_argument("--save-author", action="store_true", help="Persist resolved author URN to auth metadata.")
    p_auth_whoami.set_defaults(func=cmd_auth_whoami)

    p_auth_status = auth_sub.add_parser("status", help="Show LinkedIn auth status.")
    p_auth_status.set_defaults(func=cmd_auth_status)

    p_auth_revoke = auth_sub.add_parser("revoke", help="Revoke local LinkedIn auth metadata and token references.")
    p_auth_revoke.set_defaults(func=cmd_auth_revoke)

    p_post = subcommands.add_parser("post", help="LinkedIn posting and retrieval operations.")
    post_sub = p_post.add_subparsers(dest="post_command", required=True)

    p_post_create = post_sub.add_parser("create", help="Create a LinkedIn post.")
    p_post_create.add_argument("--author-urn", help="Author URN; defaults to saved auth metadata.")
    p_post_create.add_argument("--text", help="Post text.")
    p_post_create.add_argument("--text-file", help="Load post text from file.")
    p_post_create.add_argument("--stdin", action="store_true", help="Read post text from stdin.")
    p_post_create.add_argument("--link", help="Optional article/demo link.")
    p_post_create.add_argument("--title", help="Optional link title.")
    p_post_create.add_argument("--description", help="Optional link description.")
    p_post_create.add_argument("--visibility", choices=("PUBLIC", "CONNECTIONS"), default="PUBLIC")
    p_post_create.add_argument("--schedule-at", help="Optional ISO-8601 schedule time for downstream workers.")
    p_post_create.set_defaults(func=cmd_post_create)

    p_post_get = post_sub.add_parser("get", help="Get post details by URN.")
    p_post_get.add_argument("--post-urn", required=True, help="Post URN (e.g. urn:li:ugcPost:123).")
    p_post_get.add_argument("--source", choices=("remote", "ledger", "both"), default="both")
    p_post_get.set_defaults(func=cmd_post_get)

    p_post_list = post_sub.add_parser("list", help="List posts for an author (remote and/or ledger).")
    p_post_list.add_argument("--author-urn", help="Author URN; defaults to saved auth metadata.")
    p_post_list.add_argument("--count", type=int, default=10, help="Remote page size.")
    p_post_list.add_argument("--start", type=int, default=0, help="Remote pagination start.")
    p_post_list.add_argument("--limit", type=int, default=20, help="Local ledger result cap.")
    p_post_list.add_argument("--source", choices=("remote", "ledger", "both"), default="remote")
    p_post_list.set_defaults(func=cmd_post_list)

    p_post_history = post_sub.add_parser("history", help="Read local post receipt history.")
    p_post_history.add_argument("--limit", type=int, default=20)
    p_post_history.add_argument("--post-urn", help="Filter by post URN.")
    p_post_history.add_argument("--author-urn", help="Filter by author URN.")
    p_post_history.add_argument("--contains", help="Case-insensitive substring filter.")
    p_post_history.set_defaults(func=cmd_post_history)

    p_analytics = subcommands.add_parser("analytics", help="Post analytics retrieval operations.")
    analytics_sub = p_analytics.add_subparsers(dest="analytics_command", required=True)
    p_analytics_get = analytics_sub.add_parser("get", help="Fetch engagement metrics for a post URN.")
    p_analytics_get.add_argument("--post-urn", required=True, help="Target post URN.")
    p_analytics_get.set_defaults(func=cmd_analytics_get)

    p_completion = subcommands.add_parser("completion", help="Print shell completion helper snippet.")
    p_completion.add_argument("--shell", choices=("bash", "zsh", "fish"), default="bash")
    p_completion.set_defaults(func=cmd_completion)

    return parser


def make_context(args: argparse.Namespace) -> Context:
    cfg = load_effective_config(args)

    profile = args.profile or cfg["defaults"].get("profile", "default")
    output_mode = "human"
    if args.json:
        output_mode = "json"
    elif args.plain:
        output_mode = "plain"
    else:
        output_mode = cfg["defaults"].get("output_mode", "human")

    no_color_env = os.environ.get("NO_COLOR") is not None or os.environ.get("TERM") == "dumb"
    no_color = bool(args.no_color or no_color_env)

    no_input_cfg = False
    env_no_input = os.environ.get("LINKEDIN_CLI_NO_INPUT")
    if env_no_input:
        try:
            no_input_cfg = parse_bool(env_no_input)
        except ValueError as exc:
            raise CLIError(str(exc), EXIT_CONFIG) from exc
    no_input = bool(args.no_input or no_input_cfg)

    token_store = expand_path(cfg["paths"]["token_store"])
    secrets_dir = expand_path(cfg["paths"]["secrets_dir"])
    jobs_dir = expand_path(cfg["paths"]["jobs_dir"])
    ledger_path = expand_path(cfg["paths"]["ledger_path"])

    return Context(
        profile=profile,
        output_mode=output_mode,
        quiet=args.quiet,
        verbose=args.verbose,
        no_color=no_color,
        no_input=no_input,
        dry_run=args.dry_run,
        force=args.force,
        enqueue=args.enqueue,
        config=cfg,
        token_store=token_store,
        secrets_dir=secrets_dir,
        jobs_dir=jobs_dir,
        ledger_path=ledger_path,
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        ctx = make_context(args)
        if not hasattr(args, "func"):
            raise CLIError("No subcommand selected.", EXIT_USAGE)
        result: CommandResult = args.func(ctx, args)
        emit_result(ctx, result)
        return EXIT_SUCCESS
    except CLIError as exc:
        output_mode = "json" if "--json" in (argv or sys.argv) else "human"
        if "--plain" in (argv or sys.argv):
            output_mode = "plain"
        emit_error(output_mode, str(exc), exc.code, exc.details)
        return exc.code
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return EXIT_INTERRUPTED
    except Exception as exc:  # pragma: no cover - guardrail for unexpected failures
        emit_error("human", f"Unexpected failure: {exc}", EXIT_GENERIC)
        return EXIT_GENERIC


if __name__ == "__main__":
    sys.exit(main())
