import grpc
from _grpc.url_encoder_pb2_grpc import UrlEncoderStub
from _grpc.url_encoder_pb2 import EncodeReq

if __name__ == "__main__":
    client = UrlEncoderStub(
        grpc.insecure_channel( "localhost:50051" )
    )

    print( client.encode( EncodeReq() ).encoded )