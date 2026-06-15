# raspi-esp32-status-panel

Raspberry Pi と ESP32 を組み合わせたハードウェアステータスパネル。

- **hub/** — Raspberry Pi 上で動く HTTP サーバー。各サービスの JSON データを集約して ESP32 に返す。
- **esp32/** — ESP32 上で動く MicroPython クライアント。ハブからデータを取得し OLED に表示する。

## ハードウェア構成

**Raspberry Pi**
- BME280 センサー（温度・湿度・気圧）

**ESP32**
- SSD1306 OLED（128x64, I2C）
  - SDA: GPIO 21
  - SCL: GPIO 22
- タクトスイッチ: GPIO 13（画面切り替え）
- スライドスイッチ: GPIO 14（レイヤー切り替え）

## ハブのセットアップ（Raspberry Pi）

### 1. リポジトリをクローン

```bash
cd ~
git clone https://github.com/na2ki/raspi-esp32-status-panel.git
cd raspi-esp32-status-panel/hub
```

### 2. venv と Flask のインストール

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 動作確認

```bash
source venv/bin/activate
python3 main.py
```

別ターミナルから確認：

```bash
curl http://localhost:8080/screens
```

### 4. systemd サービス設定（自動起動）

サービスファイルを作成：

```bash
sudo cp ~/raspi-esp32-status-panel/systemd/raspi-hub.service.example /etc/systemd/system/raspi-hub.service
sudo nano /etc/systemd/system/raspi-hub.service
```

`<USER>` をログインユーザー名に書き換える。

有効化：

```bash
sudo systemctl daemon-reload
sudo systemctl enable raspi-hub.service
sudo systemctl start raspi-hub.service
```

## ESP32 のセットアップ

### 1. MicroPython のインストール

[Thonny](https://thonny.org/) を使って ESP32 に MicroPython をフラッシュする。

### 2. ssd1306.py の取得

[micropython-lib](https://github.com/micropython/micropython-lib/blob/master/micropython/drivers/display/ssd1306/ssd1306.py) から `ssd1306.py` をダウンロードする。

### 3. ファイルのアップロード

Thonny で以下のファイルを ESP32 にアップロードする：

| ファイル | 取得元 |
|---|---|
| `esp32/main.py` | このリポジトリ |
| `esp32/display.py` | このリポジトリ |
| `esp32/bfont.py` | このリポジトリ |
| `esp32/jpfont.bin` | このリポジトリ（256KB） |
| `ssd1306.py` | micropython-lib |

### 4. config.py の作成

`esp32/config.py.example` を参考に、**Thonny 上で直接** `config.py` を作成する（リポジトリにはコミットしない）：

```python
WIFI_SSID = 'your_wifi_ssid'
WIFI_PASSWORD = 'your_wifi_password'
HUB_URL = 'http://192.168.x.x:8080/screens'
POLL_INTERVAL = 1.5
```

## データソースの追加

各サービスは `hub/data/<サービス名>.json` に書き込む。ファイル名がそのまま画面 ID になる。

フォーマット：

```json
{
  "updated_at": "2024-01-01T12:34:56",
  "lines": ["行1", "行2", "行3", "行4"]
}
```

- `lines` は 4 要素固定。空行は `""` で埋める
- `updated_at` は ISO 8601 形式（ローカル時刻）
- アトミック write（一時ファイル → リネーム）を推奨

## VRChat 通知との連携

[vrchat_friendnotify_prd](https://github.com/na2ki/vrchat_friendnotify_prd) を使う場合、`HUB_DATA_DIR` 環境変数にハブの data ディレクトリのパスを設定する：

```
HUB_DATA_DIR=/home/<USER>/raspi-esp32-status-panel/hub/data
```

## 日本語フォントについて

`esp32/jpfont.bin` は IPAex ゴシックから生成したビットマップフォントファイルです（IPA フォントライセンス）。

フォントを再生成する場合は `tools/font_convert.py` のコメントを参照してください。
