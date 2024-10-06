FROM python:3.12.7-slim-bookworm

RUN apt-get update && apt-get install -y gcc

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir grpcio grpcio-tools