# AGENTS.md

このファイルには `switchbot_scene_bridge` 固有のルールだけを記載します。ワークスペース共通ルールは親ディレクトリの `AGENTS.md` を参照します。

## プロジェクト概要

SwitchBot OpenAPI v1.1 の manual scene を取得し、Home Assistant の button entity とサービスとして公開するカスタム統合です。

- domain: `switchbot_scene_bridge`
- 実装: `custom_components/switchbot_scene_bridge/`
- 設定例: `ha_config/`
- 補助スクリプト: `scripts/switchbot_scene.py`

## 固有の制約

- OpenAPI token と secret は `secrets.yaml` または config entry から渡し、`secrets.additions.yaml` にはプレースホルダーだけを置きます。
- SwitchBot の署名は token、secret、時刻、nonce の組み合わせに依存します。署名方式とヘッダー名は OpenAPI v1.1 の仕様と既存 `api.py` を正本として扱います。
- coordinator の scene 一覧を entity とサービスで共有し、同じ取得処理を重複実装しません。
- scene 実行は実機状態を変えます。通常の疎通では scene 一覧取得までに留め、実行 API は対象 scene を確認してから呼びます。
- `ha_config/configuration.yaml` と `scripts.yaml` は本番ファイル全体の置換用ではなく、統合する断片です。
- `ha_config/` には HDMI capture など他機能の例も含まれるため、SwitchBot 変更のついでに本番へ一括反映しません。

## 検証

```sh
python3 -m compileall custom_components/switchbot_scene_bridge scripts
```

実機反映時は `custom_components/switchbot_scene_bridge/` と、意図的に選んだ設定断片だけを対象にします。
