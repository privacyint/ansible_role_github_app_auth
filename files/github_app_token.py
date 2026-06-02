#!/usr/bin/env python3
"""Generate/reuse a GitHub App installation token with optional local caching.

This script is intentionally self-contained so the role logic
is testable outside inline shell snippets.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any

import jwt  # type: ignore[import-not-found]
import requests  # type: ignore[import-untyped]


class TokenError(Exception):
    """Raised for token generation/acquisition failures."""


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="GitHub App installation token helper"
    )
    parser.add_argument("--app-id", required=True)
    parser.add_argument("--installation-id", required=True)
    parser.add_argument("--private-key-b64", required=True)
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--ttl-seconds", type=int, default=3600)
    parser.add_argument("--refresh-buffer-seconds", type=int, default=300)
    parser.add_argument(
        "--cache-enabled", choices=["true", "false"], default="true"
    )
    parser.add_argument("--cache-file", required=True)
    return parser.parse_args()


def _load_cache(cache_file: Path) -> dict[str, Any] | None:
    if not cache_file.exists():
        return None

    try:
        data = json.loads(cache_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None

    if not isinstance(data, dict):
        return None

    if not all(key in data for key in ("token", "expires_at")):
        return None

    return data


def _cache_is_valid(data: dict[str, Any], refresh_buffer_seconds: int) -> bool:
    try:
        expires_at = dt.datetime.fromisoformat(
            str(data["expires_at"]).replace("Z", "+00:00")
        )
    except ValueError:
        return False

    now = dt.datetime.now(dt.timezone.utc)
    return now + dt.timedelta(seconds=refresh_buffer_seconds) < expires_at


def _write_cache(cache_file: Path, payload: dict[str, Any]) -> None:
    cache_file.parent.mkdir(mode=0o700, parents=True, exist_ok=True)

    tmp_file = cache_file.with_suffix(".tmp")
    tmp_file.write_text(json.dumps(payload), encoding="utf-8")
    os.chmod(tmp_file, stat.S_IRUSR | stat.S_IWUSR)
    tmp_file.replace(cache_file)


def _build_jwt(app_id: str, private_key_b64: str, ttl_seconds: int) -> str:
    now = int(dt.datetime.now(dt.timezone.utc).timestamp())

    try:
        private_key = base64.b64decode(private_key_b64).decode("utf-8")
    except (ValueError, UnicodeDecodeError) as exc:
        raise TokenError("Unable to decode github_private_key_b64") from exc

    payload = {
        "iat": now - 60,
        "exp": now + min(ttl_seconds, 600),
        "iss": app_id,
    }

    try:
        encoded = jwt.encode(payload, private_key, algorithm="RS256")
    except Exception as exc:  # noqa: BLE001
        raise TokenError("Unable to sign GitHub App JWT") from exc

    return encoded if isinstance(encoded, str) else encoded.decode("utf-8")


def _request_installation_token(
    api_url: str, installation_id: str, app_jwt: str
) -> dict[str, Any]:
    token_url = (
        f"{api_url.rstrip('/')}/app/installations/"
        f"{installation_id}/access_tokens"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {app_jwt}",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    response = requests.post(token_url, headers=headers, timeout=30)
    if response.status_code >= 400:
        raise TokenError(
            f"GitHub token request failed: HTTP {response.status_code}"
        )

    data = response.json()
    if "token" not in data or "expires_at" not in data:
        raise TokenError("GitHub token response missing expected fields")

    return {
        "token": data["token"],
        "expires_at": data["expires_at"],
    }


def main() -> int:
    args = _parse_args()

    cache_enabled = args.cache_enabled == "true"
    cache_file = Path(args.cache_file)

    if cache_enabled:
        cached = _load_cache(cache_file)
        if cached and _cache_is_valid(cached, args.refresh_buffer_seconds):
            print(
                json.dumps(
                    {
                        "token": cached["token"],
                        "expires_at": cached["expires_at"],
                        "source": "cache",
                    }
                )
            )
            return 0

    try:
        app_jwt = _build_jwt(
            args.app_id, args.private_key_b64, args.ttl_seconds
        )
        fresh = _request_installation_token(
            args.api_url, args.installation_id, app_jwt
        )
    except TokenError as exc:
        print(json.dumps({"error": str(exc)}))
        return 1

    if cache_enabled:
        _write_cache(cache_file, fresh)

    print(
        json.dumps(
            {
                "token": fresh["token"],
                "expires_at": fresh["expires_at"],
                "source": "fresh",
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
