#!/usr/bin/env python3
"""
MinIO バケット管理ツール

機能:
- .envファイルからバケット名配列を読み込み
- 複数バケットの一括作成
- バケット一覧表示
- バケット削除（オプション）
"""

import os
import sys
import json
import subprocess
import re
import argparse
from typing import List, Dict
from dotenv import load_dotenv
from minio import Minio
from minio.error import S3Error


class BucketManager:
    """
    BucketManager

    MinIOバケットの管理を行うクラス。

    主な機能:
    - 環境変数からMinIO接続情報とバケット名リストを読み込み、初期化
    - MinIOサーバーへの接続確認
    - mcコマンドによるエイリアス設定
    - バケット名のバリデーション（MinIO命名規則準拠）
    - バケット一覧の取得・表示
    - バケットの存在確認・作成・削除
    - 環境変数で指定された複数バケットの一括作成
    - 設定されたバケットの状態表示

    Attributes:
        endpoint (str): MinIOサーバーのエンドポイント
        root_user (str): MinIO管理ユーザー名
        root_password (str): MinIO管理ユーザーパスワード
        alias (str): mcコマンド用エイリアス名
        bucket_names (List[str]): 管理対象バケット名リスト

    Methods:
        __init__(): 環境変数の読み込みと設定の初期化
        validate_bucket_name(bucket_name): バケット名のバリデーション
        check_minio_connection(): MinIOサーバーへの接続確認
        setup_mc_alias(): mcコマンドのエイリアス設定
        initialize(): 初期化処理（接続確認 + エイリアス設定 + バリデーション）
        list_buckets(): バケット一覧の取得
        bucket_exists(bucket_name): 指定バケットの存在確認
        create_bucket(bucket_name): 単一バケットの作成
        create_buckets_from_env(): 環境変数で設定されたバケットを一括作成
        delete_bucket(bucket_name, force): バケット削除
        show_buckets(): バケット一覧を表形式で表示
        show_target_buckets_status(): 設定されたバケットの状態表示
    """

    def __init__(self):
        """環境変数の読み込みと設定の初期化"""
        load_dotenv()

        # 必須環境変数
        self.endpoint = os.getenv('MINIO_ENDPOINT')
        self.root_user = os.getenv('MINIO_ROOT_USER')
        self.root_password = os.getenv('MINIO_ROOT_PASSWORD')
        self.alias = os.getenv('MINIO_ALIAS', 'myminio')

        # バケット設定（新規）
        buckets_str = os.getenv('MINIO_BUCKETS', '')
        self.bucket_names = [name.strip()
                             for name in buckets_str.split(',') if name.strip()]

        # 設定検証
        if not all([self.endpoint, self.root_user, self.root_password]):
            raise ValueError(
                "必須の環境変数が設定されていません（MINIO_ENDPOINT, MINIO_ROOT_USER, MINIO_ROOT_PASSWORD）")

        if not self.bucket_names:
            raise ValueError("MINIO_BUCKETSが設定されていません")

        print("🔧 設定読み込み完了:")
        print(f"   - Endpoint: {self.endpoint}")
        print(f"   - Alias: {self.alias}")
        print(f"   - Target Buckets: {self.bucket_names}")

    def validate_bucket_name(self, bucket_name: str) -> bool:
        """
        バケット名のバリデーション
        MinIOの命名規則:
        - 小文字英数字、ハイフンのみ
        - 3-63文字
        - 先頭末尾はピリオド不可
        """
        if not (3 <= len(bucket_name) <= 63):
            print(f"❌ バケット名 '{bucket_name}': 長さは3-63文字である必要があります")
            return False

        if not re.match(r'^[a-z0-9.-]+$', bucket_name):
            print(f"❌ バケット名 '{bucket_name}': 小文字英数字、ハイフン、ピリオドのみ使用可能です")
            return False

        if bucket_name.startswith('.') or bucket_name.endswith('.'):
            print(f"❌ バケット名 '{bucket_name}': ピリオドで開始・終了することはできません")
            return False

        return True

    def check_minio_connection(self) -> bool:
        """MinIOサーバーへの接続確認"""
        try:
            # エンドポイントからプロトコルとホスト部分を抽出
            endpoint_clean = self.endpoint.replace(
                'http://', '').replace('https://', '')
            secure = self.endpoint.startswith('https://')

            client = Minio(
                endpoint_clean,
                access_key=self.root_user,
                secret_key=self.root_password,
                secure=secure
            )

            # 接続テスト（バケット一覧取得）
            list(client.list_buckets())
            print("✅ MinIOサーバー接続確認: 成功")
            return True

        except S3Error as e:
            print(f"❌ MinIOサーバー接続確認: 失敗 - {e}")
            return False
        except Exception as e:
            print(f"❌ MinIOサーバー接続確認: 予期しないエラー - {e}")
            return False

    def setup_mc_alias(self) -> bool:
        """mcコマンドのエイリアス設定"""
        try:
            cmd = [
                'mc', 'alias', 'set', self.alias,
                self.endpoint, self.root_user, self.root_password
            ]

            subprocess.run(
                cmd, capture_output=True, text=True, check=True)
            print("✅ mcエイリアス設定: 成功")
            return True

        except subprocess.CalledProcessError as e:
            print("❌ mcエイリアス設定: 失敗")
            print(f"   Command: {' '.join(cmd)}")
            print(f"   Error: {e.stderr}")
            return False

    def initialize(self) -> bool:
        """初期化処理（接続確認 + エイリアス設定）"""
        print("🚀 BucketManager 初期化開始...")

        if not self.check_minio_connection():
            return False

        if not self.setup_mc_alias():
            return False

        # バケット名のバリデーション
        for bucket_name in self.bucket_names:
            if not self.validate_bucket_name(bucket_name):
                return False

        print("✅ 初期化完了")
        return True

    def list_buckets(self) -> List[Dict]:
        """バケット一覧の取得"""
        try:
            cmd = ['mc', 'ls', f'{self.alias}/', '--json']
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True)

            buckets = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        bucket_info = json.loads(line)
                        if bucket_info.get('type') == 'folder':
                            buckets.append({
                                'name': bucket_info.get('key', '').rstrip('/'),
                                'lastModified': bucket_info.get('lastModified'),
                                'size': bucket_info.get('size', 0)
                            })
                    except json.JSONDecodeError:
                        continue

            return buckets

        except subprocess.CalledProcessError as e:
            print(f"❌ バケット一覧取得エラー: {e.stderr}")
            return []

    def bucket_exists(self, bucket_name: str) -> bool:
        """指定バケットの存在確認"""
        try:
            cmd = ['mc', 'ls', f'{self.alias}/{bucket_name}/', '--json']
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False)
            return result.returncode == 0
        except Exception:
            return False

    def create_bucket(self, bucket_name: str) -> bool:
        """単一バケットの作成"""
        try:
            if self.bucket_exists(bucket_name):
                print(f"ℹ️  バケット '{bucket_name}' は既に存在します")
                return True

            cmd = ['mc', 'mb', f'{self.alias}/{bucket_name}']
            subprocess.run(
                cmd, capture_output=True, text=True, check=True)

            print(f"✅ バケット '{bucket_name}' 作成成功")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ バケット '{bucket_name}' 作成失敗")
            print(f"   Error: {e.stderr}")
            return False

    def create_buckets_from_env(self) -> bool:
        """環境変数で設定されたバケットを一括作成"""
        print(f"🪣 バケット一括作成開始（対象: {len(self.bucket_names)}個）")

        success_count = 0
        for bucket_name in self.bucket_names:
            print(f"\n📦 バケット '{bucket_name}' 作成中...")
            if self.create_bucket(bucket_name):
                success_count += 1

        print(f"\n📊 作成結果: {success_count}/{len(self.bucket_names)} 成功")
        return success_count == len(self.bucket_names)

    def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """バケット削除（オプション機能）"""
        try:
            if not self.bucket_exists(bucket_name):
                print(f"⚠️  バケット '{bucket_name}' は存在しません")
                return True

            cmd = ['mc', 'rb', f'{self.alias}/{bucket_name}']
            if force:
                cmd.append('--force')

            subprocess.run(
                cmd, capture_output=True, text=True, check=True)
            print(f"✅ バケット '{bucket_name}' 削除成功")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ バケット '{bucket_name}' 削除失敗")
            print(f"   Error: {e.stderr}")
            return False

    def show_buckets(self):
        """バケット一覧を見やすい表形式で表示"""
        buckets = self.list_buckets()

        if not buckets:
            print("📭 バケットが見つかりませんでした")
            return

        print(f"\n📋 バケット一覧 (合計: {len(buckets)}個)")
        print("=" * 80)
        print(f"{'バケット名':<30} {'最終更新':<25} {'サイズ':<15}")
        print("-" * 80)

        for bucket in buckets:
            name = bucket['name'][:28] + \
                '...' if len(bucket['name']) > 30 else bucket['name']
            last_modified = bucket.get(
                'lastModified', 'N/A')[:24] if bucket.get('lastModified') else 'N/A'
            size = f"{bucket.get('size', 0):,} bytes" if bucket.get(
                'size') else '0 bytes'

            print(f"{name:<30} {last_modified:<25} {size:<15}")

        print("=" * 80)

    def show_target_buckets_status(self):
        """設定されたバケットの現在の状態を表示"""
        print("\n🎯 設定バケットの状態確認")
        print("=" * 60)

        for bucket_name in self.bucket_names:
            exists = self.bucket_exists(bucket_name)
            status = "✅ 存在" if exists else "❌ 未作成"
            print(f"{bucket_name:<30} {status}")

        print("=" * 60)


def main():
    """メイン実行関数"""

    parser = argparse.ArgumentParser(description='MinIO バケット管理ツール')
    parser.add_argument('--create', action='store_true',
                        help='環境変数で設定されたバケットを一括作成')
    parser.add_argument('--list', action='store_true', help='バケット一覧表示')
    parser.add_argument('--status', action='store_true', help='設定バケットの状態確認')
    parser.add_argument('--delete', type=str, help='指定バケットを削除')
    parser.add_argument('--force', action='store_true', help='削除時の強制オプション')

    args = parser.parse_args()

    try:
        manager = BucketManager()

        if not manager.initialize():
            print("❌ 初期化に失敗しました")
            sys.exit(1)

        # コマンドライン引数による処理分岐
        if args.create:
            manager.create_buckets_from_env()
        elif args.list:
            manager.show_buckets()
        elif args.status:
            manager.show_target_buckets_status()
        elif args.delete:
            manager.delete_bucket(args.delete, args.force)
        else:
            # デフォルト: 状態確認 + 一覧表示
            manager.show_target_buckets_status()
            manager.show_buckets()

    except KeyboardInterrupt:
        print("\n⏹️  処理を中断しました")
        sys.exit(1)


if __name__ == "__main__":
    main()
