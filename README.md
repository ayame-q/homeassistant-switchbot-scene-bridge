# SwitchBot Scene Bridge

SwitchBot OpenAPI v1.1のmanual sceneを取得し、各sceneをHome Assistantのbutton entityとサービスとして公開するカスタム統合です。

## 設定と配置

- component正本: `custom_components/switchbot_scene_bridge/`
- package正本: `switchbot_scene_bridge.yaml`
- 本番package: `/homeassistant/packages/switchbot_scene_bridge.yaml`
- secrets例: `secrets.example.yaml`

```sh
python3 ../scripts/ha_config.py deploy-component . switchbot_scene_bridge
python3 ../scripts/ha_config.py deploy-package .
```

確認後、必要なコマンドへ `--apply` を付けて反映します。`switchbot_token` と `switchbot_secret` の実値は本番の `secrets.yaml` にだけ保存します。

## 利用方法

- 生成された `button.*` entityを押してmanual sceneを実行します。
- または `switchbot_scene_bridge.execute_scene` を `scene_id` 付きで呼び出します。
- scene一覧は `scan_interval` に従って自動更新されます。

## 検証

```sh
python3 -m compileall custom_components/switchbot_scene_bridge scripts
```

## ライセンス

MIT License
