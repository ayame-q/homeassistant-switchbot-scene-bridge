"""Button entities for SwitchBot manual scenes."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import SwitchBotScene
from .const import DOMAIN
from .coordinator import SwitchBotSceneCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up SwitchBot scene buttons."""
    coordinator: SwitchBotSceneCoordinator = config_entry.runtime_data
    known_scene_ids: set[str] = set()

    def add_missing_entities() -> None:
        new_scene_ids = set(coordinator.data or {}) - known_scene_ids
        if not new_scene_ids:
            return
        known_scene_ids.update(new_scene_ids)
        async_add_entities(
            SwitchBotSceneButton(coordinator, scene_id)
            for scene_id in sorted(new_scene_ids)
        )

    add_missing_entities()
    config_entry.async_on_unload(coordinator.async_add_listener(add_missing_entities))


class SwitchBotSceneButton(CoordinatorEntity[SwitchBotSceneCoordinator], ButtonEntity):
    """Button that executes one SwitchBot manual scene."""

    _attr_has_entity_name = False

    def __init__(
        self,
        coordinator: SwitchBotSceneCoordinator,
        scene_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._scene_id = scene_id
        self._attr_unique_id = f"{DOMAIN}_{scene_id}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "manual_scenes")},
            "name": "SwitchBot Manual Scenes",
            "manufacturer": "SwitchBot",
            "model": "OpenAPI v1.1 Manual Scenes",
        }

    @property
    def scene(self) -> SwitchBotScene | None:
        """Return the latest scene metadata."""
        return (self.coordinator.data or {}).get(self._scene_id)

    @property
    def name(self) -> str:
        """Return the scene button name."""
        if scene := self.scene:
            return scene.name
        return self._scene_id

    @property
    def available(self) -> bool:
        """Return true when the scene still exists in SwitchBot."""
        return self.scene is not None

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        """Return SwitchBot scene metadata."""
        return {"scene_id": self._scene_id}

    async def async_press(self) -> None:
        """Execute the SwitchBot manual scene."""
        await self.coordinator.api.async_execute_scene(self._scene_id)
        await self.coordinator.async_request_refresh()
