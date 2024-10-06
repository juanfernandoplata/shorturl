import grpc
from _grpc.url_encoder_pb2_grpc import UrlEncoderStub
from _grpc.url_encoder_pb2 import EncodeReq

import tsl

from time import sleep

if __name__ == "__main__":
    sleep( 5 )

    credentials = grpc.ssl_channel_credentials(
        root_certificates = tsl.ROOT_CERTIFICATES,
        certificate_chain = tsl.CLIENT_CERTIFICATE,
        private_key = tsl.CLIENT_KEY,
    )

    client = UrlEncoderStub(
        grpc.secure_channel( "localhost:50051", credentials )
    )

    print( client.encode( EncodeReq() ).encoded )