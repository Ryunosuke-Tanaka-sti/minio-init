# .devcontainer/Dockerfile
FROM mcr.microsoft.com/devcontainers/python:3.11

# uvをインストール（公式スクリプト経由）
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# uvをシステム全体で使えるようにする
RUN cp /root/.cargo/bin/uv /usr/local/bin/uv || \
    (echo "uv not found in expected location, trying alternative install..." && \
     curl -LsSf https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-unknown-linux-gnu.tar.gz | \
     tar -xz -C /tmp && \
     mv /tmp/uv-x86_64-unknown-linux-gnu/uv /usr/local/bin/uv && \
     chmod +x /usr/local/bin/uv)

# MinIO Client (mc) をインストール
RUN curl -L https://dl.min.io/client/mc/release/linux-amd64/mc \
    -o /usr/local/bin/mc && \
    chmod +x /usr/local/bin/mc

# 作業ディレクトリを設定
WORKDIR /workspace

# Pythonパッケージのアップグレード
RUN pip install --upgrade pip

# mcが正しくインストールされたか確認
RUN mc --version

USER vscode