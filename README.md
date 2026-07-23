# SwitchBot Scene Bridge for Home Assistant

This staged bundle adds a custom Home Assistant integration that discovers
SwitchBot OpenAPI v1.1 manual scenes and exposes each scene as a Home Assistant
button entity.

Files to transfer:

- `custom_components/switchbot_scene_bridge/` -> `/config/custom_components/switchbot_scene_bridge/`
- `ha_config/configuration.yaml` -> `/config/configuration.yaml`
- `ha_config/scripts.yaml` -> `/config/scripts.yaml`

Manual secret setup after transfer:

1. Add the value-only entries from `ha_config/secrets.additions.yaml` to `/config/secrets.yaml`.
2. Replace `REPLACE_WITH_SWITCHBOT_OPEN_TOKEN` and `REPLACE_WITH_SWITCHBOT_SECRET`.
3. Restart Home Assistant.

Usage:

- Press the generated `button.*` entity for a SwitchBot manual scene.
- Or call `switchbot_scene_bridge.execute_scene` with a `scene_id`.

Scenes are refreshed automatically based on `scan_interval` in
`configuration.yaml`.
