"""Config flow for SwitchBot Scene Bridge."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SwitchBotApiError, SwitchBotSceneApi
from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SECRET,
    CONF_TOKEN,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)


class SwitchBotSceneBridgeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle SwitchBot Scene Bridge config flows."""

    VERSION = 1

    async def async_step_import(
        self,
        import_config: dict[str, Any],
    ) -> config_entries.ConfigFlowResult:
        """Import YAML configuration."""
        await self.async_set_unique_id("switchbot_scene_bridge")
        self._abort_if_unique_id_configured(updates=import_config)
        return self.async_create_entry(
            title=import_config.get(CONF_NAME, DEFAULT_NAME),
            data=import_config,
        )

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle manual setup from the UI."""
        errors: dict[str, str] = {}
        if user_input is not None:
            api = SwitchBotSceneApi(
                async_get_clientsession(self.hass),
                user_input[CONF_TOKEN],
                user_input[CONF_SECRET],
            )
            try:
                await api.async_get_scenes()
            except SwitchBotApiError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id("switchbot_scene_bridge")
                self._abort_if_unique_id_configured(updates=user_input)
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_NAME),
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Required(CONF_TOKEN): str,
                    vol.Required(CONF_SECRET): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL,
                    ): int,
                }
            ),
            errors=errors,
        )
