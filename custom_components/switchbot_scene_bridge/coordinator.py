"""Data coordinator for SwitchBot Scene Bridge."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SwitchBotApiError, SwitchBotScene, SwitchBotSceneApi
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class SwitchBotSceneCoordinator(DataUpdateCoordinator[dict[str, SwitchBotScene]]):
    """Fetch and cache SwitchBot manual scenes."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: SwitchBotSceneApi,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, SwitchBotScene]:
        try:
            scenes = await self.api.async_get_scenes()
        except SwitchBotApiError as err:
            raise UpdateFailed(str(err)) from err

        return {scene.scene_id: scene for scene in scenes}
