# MinIO管理ツール

MinIOのアクセスキーとバケットを管理するためのPythonツール集です。

## 📋 概要

このツールセットは以下の機能を提供します：

- **アクセスキー管理**: MinIOのアクセスキーの作成、一覧表示、削除、詳細確認
- **バケット管理**: MinIOバケットの一括作成、一覧表示、状態確認、削除

## 🏗️ プロジェクト構造

```
.
├── README.md
├── pyproject.toml
├── src
│   ├── access_key_manager.py    # アクセスキー管理ツール
│   └── bucket_manager.py        # バケット管理ツール
└── uv.lock
```

## 🚀 セットアップ

### 必要要件

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) パッケージマネージャー
- [MinIO Client (mc)](https://min.io/docs/minio/linux/reference/minio-mc.html)

### インストール

1. **リポジトリのクローン**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **依存関係のインストール**
   ```bash
   uv sync
   ```

3. **MinIO Clientのインストール**
   ```bash
   # Linux/macOS
   curl https://dl.min.io/client/mc/release/linux-amd64/mc \
     --create-dirs \
     -o $HOME/minio-binaries/mc
   chmod +x $HOME/minio-binaries/mc
   export PATH=$PATH:$HOME/minio-binaries/

   # またはパッケージマネージャーを使用
   # Ubuntu/Debian
   wget https://dl.min.io/client/mc/release/linux-amd64/mc
   chmod +x mc
   sudo mv mc /usr/local/bin/
   ```

### 環境変数設定

プロジェクトルートに `.env` ファイルを作成します：

```env
# MinIO接続情報（必須）
MINIO_ENDPOINT=http://minio:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
MINIO_ALIAS=myminio

# アクセスキー設定（オプション）
MINIO_ACCESS_KEY_NAME=minioadmin

# バケット設定（必須 - bucket_manager使用時）
MINIO_BUCKETS=bucket-data,bucket-logs,bucket-backup
```

#### 環境変数説明

| 変数名 | 必須 | 説明 | デフォルト値 |
|--------|------|------|--------------|
| `MINIO_ENDPOINT` | ✅ | MinIOサーバーのエンドポイント | なし |
| `MINIO_ROOT_USER` | ✅ | MinIO管理者ユーザー名 | なし |
| `MINIO_ROOT_PASSWORD` | ✅ | MinIO管理者パスワード | なし |
| `MINIO_ALIAS` | ❌ | mcコマンド用エイリアス名 | `myminio` |
| `MINIO_ACCESS_KEY_NAME` | ❌ | デフォルトアクセスキー名 | `no-name` |
| `MINIO_BUCKETS` | ⚠️ | 管理対象バケット名（カンマ区切り） | なし（bucket_manager使用時は必須） |

## 🔑 アクセスキー管理ツール

### 基本的な使用方法

```bash
# 仮想環境でスクリプトを実行
uv run src/access_key_manager.py [オプション]
```

### 利用可能なオプション

| オプション | 説明 | 例 |
|-----------|------|-----|
| `--list` | アクセスキー一覧を表示 | `uv run src/access_key_manager.py --list` |
| `--create` | 新しいアクセスキーを作成 | `uv run src/access_key_manager.py --create` |
| `--access-key <KEY>` | 作成時にアクセスキーを指定 | `uv run src/access_key_manager.py --create --access-key mykey` |
| `--secret-key <SECRET>` | 作成時にシークレットキーを指定 | `uv run src/access_key_manager.py --create --secret-key mysecret` |
| `--name <NAME>` | アクセスキーに名前を設定 | `uv run src/access_key_manager.py --create --name "API Key"` |
| `--delete <KEY>` | 指定のアクセスキーを削除 | `uv run src/access_key_manager.py --delete mykey` |
| `--info <KEY>` | 指定のアクセスキー詳細を表示 | `uv run src/access_key_manager.py --info mykey` |

### 使用例

1. **アクセスキー一覧表示**
   ```bash
   uv run src/access_key_manager.py --list
   ```
   
2. **ランダムアクセスキーの作成**
   ```bash
   uv run src/access_key_manager.py --create --name "API Key for Application"
   ```
   
3. **指定したアクセスキーの作成**
   ```bash
   uv run src/access_key_manager.py --create \
     --access-key "myapp-access-key" \
     --secret-key "myapp-secret-key-123" \
     --name "MyApp API Key"
   ```
   
4. **アクセスキーの詳細確認**
   ```bash
   uv run src/access_key_manager.py --info "myapp-access-key"
   ```
   
5. **アクセスキーの削除**
   ```bash
   uv run src/access_key_manager.py --delete "myapp-access-key"
   ```

## 🪣 バケット管理ツール

### 基本的な使用方法

```bash
# 仮想環境でスクリプトを実行
uv run src/bucket_manager.py [オプション]
```

### 利用可能なオプション

| オプション | 説明 | 例 |
|-----------|------|-----|
| `--create` | 環境変数で設定されたバケットを一括作成 | `uv run src/bucket_manager.py --create` |
| `--list` | 全バケット一覧を表示 | `uv run src/bucket_manager.py --list` |
| `--status` | 設定バケットの状態確認 | `uv run src/bucket_manager.py --status` |
| `--delete <BUCKET>` | 指定バケットを削除 | `uv run src/bucket_manager.py --delete mybucket` |
| `--force` | 削除時の強制オプション | `uv run src/bucket_manager.py --delete mybucket --force` |

### 使用例

1. **設定バケットの状態確認**
   ```bash
   uv run src/bucket_manager.py --status
   ```
   
2. **環境変数で設定されたバケットの一括作成**
   ```bash
   uv run src/bucket_manager.py --create
   ```
   
3. **全バケット一覧表示**
   ```bash
   uv run src/bucket_manager.py --list
   ```
   
4. **特定バケットの削除**
   ```bash
   uv run src/bucket_manager.py --delete bucket-test
   ```
   
5. **強制削除（中身があっても削除）**
   ```bash
   uv run src/bucket_manager.py --delete bucket-test --force
   ```

## 📝 典型的な運用フロー

### 初回セットアップ

1. **環境変数の設定**
   ```bash
   # .envファイルを作成・編集
   vim .env
   ```

2. **接続確認とバケット作成**
   ```bash
   # バケット状態確認
   uv run src/bucket_manager.py --status
   
   # 設定されたバケットを一括作成
   uv run src/bucket_manager.py --create
   ```

3. **アプリケーション用アクセスキー作成**
   ```bash
   # アプリケーション用のアクセスキーを作成
   uv run src/access_key_manager.py --create \
     --name "Production API Key"
   ```

### 日常的な管理

1. **リソース状況確認**
   ```bash
   # アクセスキー一覧
   uv run src/access_key_manager.py --list
   
   # バケット一覧
   uv run src/bucket_manager.py --list
   ```

2. **新しいアクセスキーの発行**
   ```bash
   uv run src/access_key_manager.py --create --name "New Service Key"
   ```

3. **不要なリソースの削除**
   ```bash
   # アクセスキー削除
   uv run src/access_key_manager.py --delete "old-access-key"
   
   # バケット削除
   uv run src/bucket_manager.py --delete "old-bucket"
   ```

## 🛡️ セキュリティ考慮事項

- `.env` ファイルは **絶対にバージョン管理に含めない**
- アクセスキーは定期的にローテーションする
- 本番環境では最小権限の原則に従ってアクセスキーを作成する
- 不要になったアクセスキーは速やかに削除する

## 🐛 トラブルシューティング

### よくある問題と解決方法

1. **`mc` コマンドが見つからない**
   ```bash
   # mcがインストールされているか確認
   which mc
   
   # パスを通す
   export PATH=$PATH:/path/to/mc
   ```

2. **MinIOサーバーに接続できない**
   - `.env` ファイルの `MINIO_ENDPOINT` が正しいか確認
   - MinIOサーバーが起動しているか確認
   - ネットワーク接続を確認

3. **権限エラー**
   - `MINIO_ROOT_USER` と `MINIO_ROOT_PASSWORD` が正しいか確認
   - MinIOの管理者権限があるアカウントを使用しているか確認

4. **バケット名のバリデーションエラー**
   - バケット名は小文字英数字、ハイフン、ピリオドのみ使用可能
   - 3-63文字の制限
   - ピリオドで開始・終了することはできない

### デバッグモード

詳細なエラー情報が必要な場合は、以下のように実行してください：

```bash
# Pythonの詳細なエラー出力を有効にする
PYTHONPATH=src python -u src/access_key_manager.py --list

# または
PYTHONPATH=src python -u src/bucket_manager.py --status
```

## 📚 参考資料

- [MinIO Documentation](https://min.io/docs/)
- [MinIO Client (mc) Reference](https://min.io/docs/minio/linux/reference/minio-mc.html)
- [uv Documentation](https://docs.astral.sh/uv/)
