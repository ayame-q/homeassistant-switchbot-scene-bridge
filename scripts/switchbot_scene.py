#!/usr/bin/env python3
"""Run SwitchBot manual scenes through SwitchBot OpenAPI v1.1."""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


API_BASE = "https://api.switch-bot.com/v1.1"
SCENE_ID_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyz"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "0123456789"
    "-_"
)


def env_required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def signed_headers(token: str, secret: str) -> dict[str, str]:
    timestamp = str(int(time.time() * 1000))
    nonce = str(uuid.uuid4())
    message = f"{token}{timestamp}{nonce}".encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).digest()
    signature = base64.b64encode(digest).decode("utf-8")
    return {
        "Authorization": token,
        "sign": signature,
        "t": timestamp,
        "nonce": nonce,
        "Content-Type": "application/json; charset=utf8",
    }


def credential(arg_value: str | None, env_name: str) -> str:
    if arg_value:
        return arg_value.strip()
    return env_required(env_name)


def request_json(method: str, path: str, token: str, secret: str) -> dict:
    url = f"{API_BASE}{path}"
    request = urllib.request.Request(
        url,
        data=b"{}" if method == "POST" else None,
        headers=signed_headers(token, secret),
        method=method,
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"SwitchBot API HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"SwitchBot API request failed: {exc}") from exc

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"SwitchBot API returned non-JSON response: {body}") from exc

    if payload.get("statusCode") != 100:
        raise SystemExit(f"SwitchBot API error: {json.dumps(payload, ensure_ascii=False)}")
    return payload


def list_scenes(token: str, secret: str) -> int:
    payload = request_json("GET", "/scenes", token, secret)
    for scene in payload.get("body", []):
        print(f"{scene.get('sceneId')}\t{scene.get('sceneName')}")
    return 0


def execute_scene(scene_id: str, token: str, secret: str) -> int:
    scene_id = scene_id.strip()
    if not scene_id or any(char not in SCENE_ID_CHARS for char in scene_id):
        raise SystemExit("Invalid SwitchBot scene_id")

    encoded_scene_id = urllib.parse.quote(scene_id, safe="")
    request_json("POST", f"/scenes/{encoded_scene_id}/execute", token, secret)
    print(f"Executed SwitchBot scene: {scene_id}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="List SwitchBot manual scenes")
    list_parser.add_argument("--token", help="SwitchBot OpenAPI token")
    list_parser.add_argument("--secret", help="SwitchBot OpenAPI secret")
    execute = subparsers.add_parser("execute", help="Execute a SwitchBot manual scene")
    execute.add_argument("scene_id", help="SwitchBot manual scene ID")
    execute.add_argument("--token", help="SwitchBot OpenAPI token")
    execute.add_argument("--secret", help="SwitchBot OpenAPI secret")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    token = credential(args.token, "SWITCHBOT_TOKEN")
    secret = credential(args.secret, "SWITCHBOT_SECRET")
    if args.command == "list":
        return list_scenes(token, secret)
    if args.command == "execute":
        return execute_scene(args.scene_id, token, secret)
    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
