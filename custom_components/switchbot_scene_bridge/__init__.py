"""SwitchBot Scene Bridge custom integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, SOURCE_IMPORT
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .api import SwitchBotApiError, SwitchBotSceneApi
from .const import (
    CONF_SCAN_INTERVAL,
    CONF_SECRET,
    CONF_TOKEN,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import SwitchBotSceneCoordinator

SWITCHBOT_SCENE_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_TOKEN): cv.string,
        vol.Required(CONF_SECRET): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            vol.Coerce(int),
            vol.Range(min=60),
        ),
    }
)

CONFIG_SCHEMA = vol.Schema({DOMAIN: SWITCHBOT_SCENE_SCHEMA}, extra=vol.ALLOW_EXTRA)

SERVICE_EXECUTE_SCENE = "execute_scene"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up SwitchBot Scene Bridge from YAML."""
    if domain_config := config.get(DOMAIN):
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data=domain_config,
            )
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SwitchBot Scene Bridge from a config entry."""
    api = SwitchBotSceneApi(
        async_get_clientsession(hass),
        entry.data[CONF_TOKEN],
        entry.data[CONF_SECRET],
    )
    coordinator = SwitchBotSceneCoordinator(
        hass,
        api,
        entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _async_register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a SwitchBot Scene Bridge config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


def _async_register_services(hass: HomeAssistant) -> None:
    """Register integration-level services."""
    if hass.services.has_service(DOMAIN, SERVICE_EXECUTE_SCENE):
        return

    async def async_execute_scene(call: ServiceCall) -> None:
        scene_id = call.data["scene_id"]
        entries = hass.config_entries.async_entries(DOMAIN)
        if not entries:
            raise HomeAssistantError("SwitchBot Scene Bridge is not configured")

        coordinator: SwitchBotSceneCoordinator = entries[0].runtime_data
        try:
            await coordinator.api.async_execute_scene(scene_id)
        except SwitchBotApiError as err:
            raise HomeAssistantError(str(err)) from err
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_EXECUTE_SCENE,
        async_execute_scene,
        schema=vol.Schema({vol.Required("scene_id"): cv.string}),
    )
