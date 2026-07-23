"""SwitchBot OpenAPI v1.1 client for manual scenes."""

from __future__ import annotations

import base64
import hashlib
import hmac
import time
from urllib.parse import quote
import uuid
from dataclasses import dataclass
from typing import Any

from aiohttp import ClientError, ClientResponseError, ClientSession

API_BASE = "https://api.switch-bot.com/v1.1"


class SwitchBotApiError(Exception):
    """Base SwitchBot API error."""


class SwitchBotAuthError(SwitchBotApiError):
    """SwitchBot authentication failed."""


@dataclass(frozen=True)
class SwitchBotScene:
    """SwitchBot manual scene metadata."""

    scene_id: str
    name: str


class SwitchBotSceneApi:
    """Small async client for SwitchBot manual scene endpoints."""

    def __init__(self, session: ClientSession, token: str, secret: str) -> None:
        self._session = session
        self._token = token
        self._secret = secret

    def _headers(self) -> dict[str, str]:
        timestamp = str(int(time.time() * 1000))
        nonce = str(uuid.uuid4())
        message = f"{self._token}{timestamp}{nonce}".encode("utf-8")
        digest = hmac.new(
            self._secret.encode("utf-8"),
            message,
            hashlib.sha256,
        ).digest()
        signature = base64.b64encode(digest).decode("utf-8")
        return {
            "Authorization": self._token,
            "sign": signature,
            "t": timestamp,
            "nonce": nonce,
            "Content-Type": "application/json; charset=utf8",
        }

    async def _request(self, method: str, path: str) -> dict[str, Any]:
        try:
            async with self._session.request(
                method,
                f"{API_BASE}{path}",
                headers=self._headers(),
                json={} if method == "POST" else None,
                timeout=20,
            ) as response:
                response.raise_for_status()
                payload = await response.json()
        except ClientResponseError as err:
            if err.status in (401, 403):
                raise SwitchBotAuthError("SwitchBot API authentication failed") from err
            raise SwitchBotApiError(f"SwitchBot API HTTP {err.status}") from err
        except ClientError as err:
            raise SwitchBotApiError(f"SwitchBot API request failed: {err}") from err

        if payload.get("statusCode") != 100:
            message = payload.get("message", "unknown error")
            if "Unauthorized" in str(message):
                raise SwitchBotAuthError(str(message))
            raise SwitchBotApiError(f"SwitchBot API error: {message}")

        return payload

    async def async_get_scenes(self) -> list[SwitchBotScene]:
        """Return manual scenes created in the SwitchBot app."""
        payload = await self._request("GET", "/scenes")
        scenes: list[SwitchBotScene] = []
        for item in payload.get("body", []):
            scene_id = str(item.get("sceneId", "")).strip()
            scene_name = str(item.get("sceneName", "")).strip()
            if scene_id and scene_name:
                scenes.append(SwitchBotScene(scene_id=scene_id, name=scene_name))
        return scenes

    async def async_execute_scene(self, scene_id: str) -> None:
        """Execute a manual SwitchBot scene."""
        await self._request("POST", f"/scenes/{quote(scene_id, safe='')}/execute")
