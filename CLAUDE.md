# CLAUDE.md

このファイルは、Claude Code (claude.ai/code) がこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

このリポジトリは **ESP32（MicroPython）** と **Raspberry Pi HTTPハブ（Python）** のコードをまとめて管理します。

Raspberry Pi と ESP32 を役割分担するハードウェアステータスパネルシステムです。

- **esp32/（このリポジトリ）** — Raspberry Pi からデータを取得し、OLED に表示する薄いクライアント。MicroPython で実装。
- **hub/（このリポジトリ）** — 各種データソースを集約し、ESP32 に HTTP で提供するサーバー。Python で実装。
- **vrchat_friendnotify_prd（別リポジトリ）** — VRChat WebSocket を監視し、ハブにデータを送る既存サービス。Go で実装。

ESP32 側では大きな処理を行わず、重い処理はすべて Raspberry Pi 側に集約する方針。

## ハードウェア構成

**Raspberry Pi**
- BME280 センサー（温度・湿度・気圧）
- OLED 1枚目（表示内容は未定）

**ESP32**
- OLED
- タクトスイッチ — 押すごとに表示画面を切り替える
- スライドスイッチ — 画面レイヤー切り替え（キーボードのレイヤーと同じ概念）

## アーキテクチャ

### データフロー

```
各サービス（VRChat等）
    ↓ JSONファイルを書き込む
hub/data/*.json
    ↓ HTTPサーバーが読み込んで返す
ESP32（定期ポーリング）
    ↓
OLED に表示
```

### ファイルベース連携の仕様

- 各サービスは `hub/data/<サービス名>.json` に書き込む
- フォーマットは JSON（将来の拡張に備えて）
- **タイムスタンプ必須**（データの鮮度を判断するため）
- **アトミックwrite**（一時ファイルに書いてからリネーム）で中途半端な読み取りを防ぐ

JSONフォーマット（`hub/data/<サービス名>.json`）：
```json
{
  "updated_at": "2024-01-01T12:34:56",
  "lines": ["ONLINE", "FriendName", "12:34", ""]
}
```

- `updated_at` はISO 8601形式（ローカル時刻）
- `lines` は4要素固定。空行は空文字 `""` で埋める
- ファイル名がそのまま画面IDになるため `source` フィールドは不要
- ハブは古いデータも除外せずそのまま返す（最後の状態を表示し続けるため）

### 画面切り替え（ESP32）

- タクトスイッチで現在のレイヤー内の画面を順番に切り替える
- スライドスイッチでレイヤーを切り替える（画面が5枚以上になったとき活用）
- レイヤー0：画面0〜4、レイヤー1：画面5〜9（目安）

## ディレクトリ構成

```
raspi-esp32-status-panel/
├── esp32/
│   ├── main.py           ← 起動・画面切り替え・レイヤー制御
│   ├── display.py        ← OLED描画
│   ├── bfont.py          ← バイナリフォントリーダー
│   ├── jpfont.bin        ← 日本語ビットマップフォント（ESP32にアップロード）
│   └── config.py.example ← WiFi・ハブURL設定のサンプル
├── hub/
│   ├── main.py           ← HTTPサーバー（data/以下を読んで返す）
│   ├── requirements.txt  ← Python依存パッケージ
│   └── data/             ← 各サービスがJSONを書き込む場所
├── systemd/
│   └── raspi-hub.service.example ← systemdサービスファイルのテンプレート
└── tools/
    └── font_convert.py   ← jpfont.bin を再生成するスクリプト
```

## ハブ API

エンドポイントは1つ。

```
GET /screens
```

レスポンス：
```json
[
  {
    "id": "vrchat",
    "lines": ["ONLINE", "FriendName", "12:34", ""],
    "updated_at": "2024-01-01T12:34:56"
  }
]
```

- `id` はファイル名から自動生成（`vrchat.json` → `"id": "vrchat"`）
- 画面の順番はファイル名のアルファベット順

## 設定

ハブのHTTPサーバーには **Flask** を使用する。

| 設定項目 | 環境変数 | デフォルト |
|----------|----------|------------|
| data/ のパス | `HUB_DATA_DIR` | `./data` |
| ハブのポート | `HUB_PORT` | `8080` |
| ESP32のポーリング間隔 | ソースコード内の定数 | 1.5秒 |

## 未決定の設計事項

- Raspberry Pi 側 OLED に何を表示するか
- BME280 の取得値をどちら側でどう扱うか
