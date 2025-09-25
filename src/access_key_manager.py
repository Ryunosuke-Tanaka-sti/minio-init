#!/usr/bin/env python3
"""
MinIO アクセスキー管理ツール

機能:
- アクセスキーの一覧表示（name含む）
- 新しいアクセスキーの作成
- アクセスキーの削除（オプション）
- 環境変数からの設定読み込み
"""

import os
import sys
import json
import subprocess
import argparse
from typing import Dict, List, Optional
from dotenv import load_dotenv
from minio import Minio


class AccessKeyManager:
    """
    AccessKeyManager

    MinIOのアクセスキー管理を行うクラス。

    主な機能:
    - 環境変数からMinIO接続情報を読み込み、初期化
    - MinIOサーバーへの接続確認
    - mcコマンドによるエイリアス設定
    - アクセスキー一覧の取得・表示
    - アクセスキーの作成・削除

    Attributes:
        endpoint (str): MinIOサーバーのエンドポイント
        root_user (str): MinIO管理ユーザー名
        root_password (str): MinIO管理ユーザーパスワード
        alias (str): mcコマンド用エイリアス名

    Methods:
        __init__(): 環境変数の読み込みと設定の初期化
        check_minio_connection(): MinIOサーバーへの接続確認
        setup_mc_alias(): mcコマンドのエイリアス設定
        initialize(): 初期化処理（接続確認 + エイリアス設定）
        list_access_keys(): アクセスキー一覧の取得
        access_key_exists(access_key): 指定アクセスキーの存在確認
        create_access_key(): 新しいアクセスキーの作成
        delete_access_key(access_key): アクセスキーの削除
        show_access_keys(): アクセスキー一覧を表形式で表示
    """

    def __init__(self):
        """環境変数の読み込みと設定の初期化"""
        load_dotenv()

        # 必須環境変数
        self.endpoint = os.getenv("MINIO_ENDPOINT")
        self.root_user = os.getenv("MINIO_ROOT_USER")
        self.root_password = os.getenv("MINIO_ROOT_PASSWORD")
        self.alias = os.getenv("MINIO_ALIAS", "myminio")

        # 設定検証
        if not all([self.endpoint, self.root_user, self.root_password]):
            raise ValueError(
                "必須の環境変数が設定されていません（MINIO_ENDPOINT, MINIO_ROOT_USER, MINIO_ROOT_PASSWORD）"
            )

        print("🔧 設定読み込み完了:")
        print(f"   - Endpoint: {self.endpoint}")
        print(f"   - Alias: {self.alias}")

    def check_minio_connection(self) -> bool:
        """MinIOサーバーへの接続確認"""
        try:
            # エンドポイントからプロトコルとホスト部分を抽出
            endpoint_clean = self.endpoint.replace("http://", "").replace(
                "https://", ""
            )
            secure = self.endpoint.startswith("https://")

            client = Minio(
                endpoint_clean,
                access_key=self.root_user,
                secret_key=self.root_password,
                secure=secure,
            )

            # 接続テスト（バケット一覧取得）
            list(client.list_buckets())
            print("✅ MinIOサーバー接続確認: 成功")
            return True

        except Exception as e:
            print(f"❌ MinIOサーバー接続確認: 失敗 - {e}")
            return False

    def setup_mc_alias(self) -> bool:
        """mcコマンドのエイリアス設定"""
        try:
            cmd = [
                "mc",
                "alias",
                "set",
                self.alias,
                self.endpoint,
                self.root_user,
                self.root_password,
            ]

            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ mcエイリアス設定: 成功")
            return True

        except subprocess.CalledProcessError as e:
            print("❌ mcエイリアス設定: 失敗")
            print(f"   Command: {' '.join(cmd)}")
            print(f"   Error: {e.stderr}")
            return False

    def initialize(self) -> bool:
        """初期化処理（接続確認 + エイリアス設定）"""
        print("🚀 AccessKeyManager 初期化開始...")

        if not self.check_minio_connection():
            return False

        if not self.setup_mc_alias():
            return False

        print("✅ 初期化完了")
        return True

    def list_access_keys(self) -> List[Dict]:
        """アクセスキー一覧の取得（name情報を含む）"""
        try:
            cmd = [
                "mc",
                "admin",
                "user",
                "svcacct",
                "list",
                f"{self.alias}/",
                self.root_user,
                "--json",
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True)

            # JSON形式のレスポンスを解析
            if result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                access_keys = []
                for line in lines:
                    try:
                        key_info = json.loads(line)
                        key_info_detailed = self._get_detailed_key_info(
                            key_info.get("accessKey")
                        )

                        access_keys.append(key_info_detailed)
                    except json.JSONDecodeError:
                        continue
                return access_keys
        except subprocess.CalledProcessError:
            return []

    def _get_detailed_key_info(self, access_key: str) -> Optional[Dict]:
        """特定のアクセスキーの詳細情報を取得"""
        try:
            cmd = [
                "mc",
                "admin",
                "user",
                "svcacct",
                "info",
                f"{self.alias}/",
                access_key,
                "--json",
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True)

            if result.stdout.strip():
                return json.loads(result.stdout.strip())
        except (subprocess.CalledProcessError, json.JSONDecodeError):
            # 詳細情報取得に失敗した場合はNoneを返す
            pass

        return None

    def access_key_exists(self, access_key: str) -> bool:
        """指定アクセスキーの存在確認"""
        keys = self.list_access_keys()
        return any(key.get("accessKey") == access_key for key in keys)

    def create_access_key(
        self,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Optional[Dict]:
        """アクセスキーを作成"""
        try:
            if access_key and self.access_key_exists(access_key):
                print(f"ℹ️  アクセスキー '{access_key}' は既に存在します")
                return None

            cmd = [
                "mc",
                "admin",
                "user",
                "svcacct",
                "add",
                f"{self.alias}/",
                self.root_user,
            ]

            if access_key:
                cmd.extend(["--access-key", access_key])
            if secret_key:
                cmd.extend(["--secret-key", secret_key])
            if name:
                cmd.extend(["--name", name])
            else:
                default_name = os.getenv("MINIO_ACCESS_KEY_NAME", "no-name")
                cmd.extend(["--name", default_name])
            if description:
                cmd.extend(["--description", description])

            cmd.append("--json")

            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True)
            key_info = json.loads(result.stdout.strip())

            print("✅ アクセスキー作成完了!")
            print(f"   Access Key: {key_info.get('accessKey')}")
            print(f"   Secret Key: {key_info.get('secretKey')}")
            if name:
                print(f"   Name: {name}")

            return key_info

        except json.JSONDecodeError:
            print("❌ レスポンスの解析に失敗しました")
            return None

    def delete_access_key(self, access_key: str) -> bool:
        """アクセスキーの削除"""
        try:
            if not self.access_key_exists(access_key):
                print(f"⚠️  アクセスキー '{access_key}' は存在しません")
                return True

            cmd = [
                "mc",
                "admin",
                "user",
                "svcacct",
                "remove",
                f"{self.alias}/",
                access_key,
            ]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ アクセスキー '{access_key}' 削除成功")
            return True

        except subprocess.CalledProcessError:
            # 旧コマンドでフォールバック
            try:
                cmd = [
                    "mc",
                    "admin",
                    "accesskey",
                    "remove",
                    f"{self.alias}/",
                    access_key,
                ]
                subprocess.run(cmd, capture_output=True, text=True, check=True)
                print(f"✅ アクセスキー '{access_key}' 削除成功")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ アクセスキー '{access_key}' 削除失敗")
                print(f"   Error: {e.stderr}")
                return False

    def show_access_keys(self):
        """アクセスキー一覧を見やすい表形式で表示"""
        keys = self.list_access_keys()

        if not keys:
            print("📋 アクセスキーがありません")
            return

        print(f"\n📋 アクセスキー一覧 (合計: {len(keys)}件)")
        print("=" * 90)
        print(f"{'No.':<4} {'アクセスキー':<25} {'名前':<25} {'状態':<12} {'説明':<20}")
        print("-" * 90)

        for i, key in enumerate(keys, 1):
            access_key = key.get("accessKey", "N/A")
            name = key.get("name", key.get("Name", "No name"))
            status = key.get("status", key.get("accountStatus", "N/A"))
            description = key.get("description", key.get("Description", ""))

            # 表示用の文字数制限
            access_key_display = (
                access_key[:23] + "..." if len(access_key) > 25 else access_key
            )
            name_display = name[:23] + "..." if len(name) > 25 else name
            description_display = (
                description[:18] +
                "..." if len(description) > 20 else description
            )

            print(
                f"{i:<4} {access_key_display:<25} {name_display:<25} {status:<12} {description_display:<20}"
            )

        print("=" * 90)

    def get_access_key_info(self, access_key: str) -> Optional[Dict]:
        """指定されたアクセスキーの詳細情報を取得"""
        keys = self.list_access_keys()
        for key in keys:
            if key.get("accessKey") == access_key:
                return key
        return None

    def show_access_key_detail(self, access_key: str):
        """指定されたアクセスキーの詳細情報を表示"""
        key_info = self.get_access_key_info(access_key)

        if not key_info:
            print(f"❌ アクセスキー '{access_key}' が見つかりません")
            return

        print("\n🔑 アクセスキー詳細情報")
        print("=" * 60)
        print(f"Access Key:  {key_info.get('accessKey', 'N/A')}")
        print(
            f"Name:        {key_info.get('name', key_info.get('Name', 'No name'))}")
        print(
            f"Status:      {key_info.get('status', key_info.get('accountStatus', 'N/A'))}"
        )
        print(
            f"Description: {key_info.get('description', key_info.get('Description', 'No description'))}"
        )

        # 追加情報があれば表示
        if "expiration" in key_info:
            print(f"Expiration:  {key_info.get('expiration', 'N/A')}")
        if "policy" in key_info:
            print(f"Policy:      {key_info.get('policy', 'N/A')}")

        print("=" * 60)


def main():
    """メイン実行関数"""

    parser = argparse.ArgumentParser(description="MinIO アクセスキー管理ツール")
    parser.add_argument("--list", action="store_true", help="アクセスキー一覧表示")
    parser.add_argument(
        "--create", action="store_true", help="新しいアクセスキーを作成"
    )
    parser.add_argument("--access-key", type=str, help="作成時のアクセスキーを指定")
    parser.add_argument("--secret-key", type=str, help="作成時のシークレットキーを指定")
    parser.add_argument("--name", type=str, help="アクセスキーに名前を設定")
    parser.add_argument("--description", type=str, help="アクセスキーに説明を設定")
    parser.add_argument("--delete", type=str, help="指定アクセスキーを削除")
    parser.add_argument("--info", type=str, help="指定アクセスキーの詳細情報を表示")

    args = parser.parse_args()

    try:
        manager = AccessKeyManager()

        if not manager.initialize():
            print("❌ 初期化に失敗しました")
            sys.exit(1)

        # コマンドライン引数による処理分岐
        if args.create:
            print("\n🆕 新しいアクセスキーを作成:")
            manager.create_access_key(
                access_key=args.access_key, secret_key=args.secret_key, name=args.name, description=args.description
            )
        elif args.list:
            manager.show_access_keys()
        elif args.delete:
            print(f"\n🗑️  アクセスキー '{args.delete}' を削除:")
            manager.delete_access_key(args.delete)
        elif args.info:
            manager.show_access_key_detail(args.info)
        else:
            # デフォルト: アクセスキー一覧表示
            manager.show_access_keys()

    except ValueError as e:
        print(f"❌ 設定エラー: {e}")
        print("💡 .envファイルを確認してください")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  処理を中断しました")
        sys.exit(1)


if __name__ == "__main__":
    main()
