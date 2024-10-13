import grpc
from _grpc.url_encoder_pb2_grpc import UrlEncoderStub
from _grpc.url_encoder_pb2 import EncodeReq

from _grpc import tsl

from os import environ

from sharding import PgShardManager

from time import sleep

if __name__ == "__main__":
    if ( conn_strings := environ.get( "CONN_STRINGS" ) ) == None:
        print( "FATAL: environment variable CONN_STRINGS was not found" )
        exit()
    
    conn_dict = dict( zip(
        [ f"pg{i}" for i in range( 1, len( conn_strings ) ) ],
        conn_strings
    ))

    dbs = PgShardManager(
        conn_dict,
        lambda key: "pg1" if key[ -1 ] < 86 else "pg2"
    )

    credentials = grpc.ssl_channel_credentials(
        root_certificates = tsl.ROOT_CERTIFICATES,
        certificate_chain = tsl.CLIENT_CERTIFICATE,
        private_key = tsl.CLIENT_KEY,
    )

    client = UrlEncoderStub(
        grpc.secure_channel( "url-encoder:50051", credentials )
    )

    i = 1

    while( True ):
        sleep( 0.25 )

        print( f"Response {i}: {client.encode( EncodeReq() ).encoded}" )

        i += 1