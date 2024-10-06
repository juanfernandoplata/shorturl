from concurrent import futures

import grpc

from _grpc import tsl
from _grpc.url_encoder_pb2_grpc import UrlEncoderServicer, add_UrlEncoderServicer_to_server
from _grpc.url_encoder_pb2 import EncodeRes

from os import environ

import psycopg as pg
import base62

class UrlEncoder( UrlEncoderServicer ):
    def get_conn_strings( self ):
        if ( conn_strings := environ.get( "CONN_STRINGS" ) ) == None:
            print( "FATAL: environment variable CONN_STRINGS was not found" )
            exit()
        
        return conn_strings.split()
    
    def set_count( self ):
        max_short = "000000"

        for string in self.get_conn_strings():
            print( string )
            with pg.connect( string ) as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        select short
                        from url
                        order by short desc
                        limit 1
                    """)

                    if ( row := cur.fetchone() ) != None:
                        if row[ 0 ] > max_short:
                            print( "EPA" * 100 )
                            max_short = row[ 0 ]

        self.count = base62.decode( max_short )

    def __init__( self ):
        super().__init__()
        self.set_count()
    
    def gen_id( self ):
        url_id = self.count
        self.count += 1

        return url_id
    
    def gen_encoding( self ):
        return base62.encode( self.gen_id() )

    def encode( self, request, context ):
        return EncodeRes( encoded = self.gen_encoding() )

def serve():
    server = grpc.server( futures.ThreadPoolExecutor( max_workers = 1 ) )

    add_UrlEncoderServicer_to_server(
        UrlEncoder(),
        server
    )

    credentials = grpc.ssl_server_credentials(
        [ ( tsl.SERVER_CERTIFICATE_KEY, tsl.SERVER_CERTIFICATE ) ],
        root_certificates = tsl.ROOT_CERTIFICATES,
        require_client_auth = True,
    )

    server.add_secure_port( "0.0.0.0:50051", credentials )
    
    server.start()
    
    server.wait_for_termination()

if __name__ == "__main__":
    serve()