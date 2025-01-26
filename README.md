# Web予約自動化スクリプト

## システム要件
- Python 3.12以上
- Google Chrome
- ChromeDriver

## セットアップ手順

### 1. ChromeDriverのインストール
MacOSの場合：
```bash
brew install chromedriver
```

### 2. Python仮想環境のセットアップ
```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
# MacOS/Linuxの場合：
source venv/bin/activate
# Windowsの場合：
# .\venv\Scripts\activate

# 必要なパッケージのインストール
pip install -r requirements.txt
```

## 使用方法

1. 仮想環境を有効化します：
```bash
# MacOS/Linuxの場合：
source venv/bin/activate
# Windowsの場合：
# .\venv\Scripts\activate
```

2. main.pyの設定を編集します：
- `TEST_URL`：予約対象のWebサイトURL
- `TARGET_TIME`：予約実行時刻
- `FORM_DATA`：フォームに入力するデータ

3. スクリプトを実行します：
```bash
python main.py
```

## 注意事項
- ChromeDriverのバージョンは、インストールされているGoogle Chromeのバージョンと一致している必要があります。
- ヘッドレスモードで実行する場合は、`WebTest`クラスのインスタンス作成時に`headless=True`を指定してください。
- 環境変数`CHROME_DRIVER_PATH`でChromeDriverのパスを指定できます（デフォルトは'chromedriver'）。

## トラブルシューティング

### ChromeDriverが見つからない場合
1. ChromeDriverが正しくインストールされているか確認：
```bash
which chromedriver
```

2. パスが通っていない場合は、環境変数で指定：
```bash
export CHROME_DRIVER_PATH=/path/to/chromedriver
