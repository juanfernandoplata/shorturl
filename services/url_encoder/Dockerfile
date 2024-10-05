FROM python:3.12.7-slim-bookworm

WORKDIR /root

COPY ./src/ .

RUN apt-get update && apt-get install -y gcc

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir -r requirements.txt

WORKDIR /root/_base62

RUN python setup.py build && python setup.py install

WORKDIR /root

RUN python -m grpc_tools.protoc -I_grpc --grpc_python_out=_grpc --pyi_out=_grpc --python_out=_grpc _grpc/url_encoder.proto

RUN sed -i \
    '6s/.*/from .import url_encoder_pb2 as url__encoder__pb2/' \
    ./_grpc/url_encoder_pb2_grpc.py

CMD [ "python", "server.py" ]