"""Constants for SwitchBot Scene Bridge."""

from __future__ import annotations

from homeassistant.const import CONF_NAME, Platform

DOMAIN = "switchbot_scene_bridge"

CONF_SECRET = "secret"
CONF_TOKEN = "token"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_NAME = "SwitchBot Scenes"
DEFAULT_SCAN_INTERVAL = 3600

CONF_NAME_KEY = CONF_NAME

PLATFORMS: list[Platform] = [Platform.BUTTON]
