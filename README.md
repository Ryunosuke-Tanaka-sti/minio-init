# MinIO管理ツール

MinIOのアクセスキーとバケットを管理するためのPythonツール集です。

## 📋 概要

このツールセットは以下の機能を提供します：

- **アクセスキー管理**: MinIOのアクセスキーの作成、一覧表示、削除、詳細確認
- **バケット管理**: MinIOバケットの一括作成、一覧表示、状態確認、削除

## 🏗️ プロジェクト構造

```
.
├── .devcontainer
│   ├── Dockerfile           # DevContainer設定
│   ├── compose.yml          # Docker Compose（MinIOサーバー含む）
│   └── devcontainer.json    # VSCode DevContainer設定
├── .env                     # 環境変数設定ファイル
├── .gitignore
├── .python-version
├── README.md
├── pyproject.toml
├── src
│   ├── access_key_manager.py    # アクセスキー管理ツール
│   └── bucket_manager.py        # バケット管理ツール
└── uv.lock
```

## 🚀 セットアップ

### 必要要件

- **Docker** と **Docker Compose**
- **Visual Studio Code** + **Dev Containers拡張機能**

### DevContainer環境での起動

1. **リポジトリのクローン**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **VSCodeでDevContainerを開く**
   - VSCodeでプロジェクトフォルダを開く
   - `Ctrl+Shift+P` → `Dev Containers: Reopen in Container` を選択
   - DevContainerが自動的に構築され、MinIOサーバーも同時に起動

3. **依存関係のインストール**
   ```bash
   # DevContainer内で実行
   uv sync
   ```

### 環境の確認

DevContainer起動後、以下が自動的に利用可能になります：

- **Python 3.11** + **uv** + **MinIO Client (mc)** (Dockerfileで自動インストール)
- **MinIOサーバー** (Docker Compose経由で自動起動)
  - API: `http://localhost:9000`
  - Web Console: `http://localhost:9001`

### 環境変数設定

プロジェクトルートに `.env` ファイルを作成します：

```env
# MinIO接続情報（必須）
# DevContainer環境では、Dockerサービス名 "minio" を使用
MINIO_ENDPOINT=http://minio:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
MINIO_ALIAS=myminio

# アクセスキー設定（オプション）
MINIO_ACCESS_KEY_NAME=minioadmin

# バケット設定（必須 - bucket_manager使用時）
MINIO_BUCKETS=bucket-data,bucket-logs,bucket-backup
```

> **💡 DevContainer環境のポイント**
> - `MINIO_ENDPOINT` は Docker Compose のサービス名 `minio` を使用
> - MinIO Web Console は `http://localhost:9001` でアクセス可能（自動でポートフォワード）

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

1. **DevContainer環境の起動**
   ```bash
   # VSCodeでプロジェクトを開き、DevContainerで再開
   # MinIOサーバーが自動的に起動します
   ```

2. **環境変数の設定**
   ```bash
   # .envファイルを作成・編集
   vim .env
   ```

3. **MinIO Web Consoleでの確認**
   - ブラウザで `http://localhost:9001` にアクセス
   - ユーザー名: `minioadmin`, パスワード: `minioadmin123` でログイン

4. **接続確認とバケット作成**
   ```bash
   # バケット状態確認
   uv run src/bucket_manager.py --status
   
   # 設定されたバケットを一括作成
   uv run src/bucket_manager.py --create
   ```

5. **アプリケーション用アクセスキー作成**
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

1. **DevContainerが正しく起動しない**
   ```bash
   # Docker Composeサービスの状態確認
   docker-compose -f .devcontainer/compose.yml ps
   
   # MinIOサーバーの状態確認
   docker-compose -f .devcontainer/compose.yml logs minio
   
   # コンテナの再構築
   # VSCode: Ctrl+Shift+P → "Dev Containers: Rebuild Container"
   ```

2. **MinIOサーバーに接続できない**
   ```bash
   # MinIOサーバーの状態確認
   docker-compose -f .devcontainer/compose.yml ps minio
   
   # MinIOヘルスチェック
   curl -f http://localhost:9000/minio/health/live
   
   # .envファイルのENDPOINT設定確認
   cat .env | grep MINIO_ENDPOINT
   ```

3. **`mc` コマンドが見つからない**
   ```bash
   # mcがインストールされているか確認
   which mc
   mc --version
   
   # DevContainerの再構築が必要な場合があります
   ```

4. **権限エラー**
   - `.env` ファイルの `MINIO_ROOT_USER` と `MINIO_ROOT_PASSWORD` が正しいか確認
   - Docker Composeの環境変数設定と一致しているか確認

5. **バケット名のバリデーションエラー**
   - バケット名は小文字英数字、ハイフン、ピリオドのみ使用可能
   - 3-63文字の制限
   - ピリオドで開始・終了することはできない

### DevContainer固有のデバッグ

1. **MinIOサーバーログの確認**
   ```bash
   docker-compose -f .devcontainer/compose.yml logs -f minio
   ```

2. **ネットワーク接続の確認**
   ```bash
   # DevContainer内からMinIOサーバーへの接続テスト
   curl -I http://minio:9000
   
   # ポートフォワードの確認
   curl -I http://localhost:9000
   ```

3. **コンテナ内でのデバッグ**
   ```bash
   # Pythonの詳細なエラー出力を有効にする
   PYTHONPATH=src python -u src/access_key_manager.py --list
   
   # または
   PYTHONPATH=src python -u src/bucket_manager.py --status
   ```

### MinIO Web Console

DevContainer環境では以下のURLでMinIOの管理画面にアクセスできます：
- **URL**: http://localhost:9001
- **ユーザー名**: minioadmin
- **パスワード**: minioadmin123

ここで直接バケットやアクセスキーの管理も可能です。

## 📚 参考資料

- [MinIO Documentation](https://min.io/docs/)
- [MinIO Client (mc) Reference](https://min.io/docs/minio/linux/reference/minio-mc.html)
- [uv Documentation](https://docs.astral.sh/uv/)
- [VSCode Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [Docker Compose](https://docs.docker.com/compose/)

### DevContainer環境について

このプロジェクトは **VSCode Dev Containers** を使用して、一貫した開発環境を提供します：

- **Python 3.11** + **uv** + **MinIO Client** が事前インストール済み
- **MinIOサーバー** が Docker Compose 経由で自動起動
- **ポートフォワード** が自動設定（9000: API, 9001: Console）
- **VSCode拡張機能** (Python関連) が自動インストール