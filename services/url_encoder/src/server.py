from concurrent import futures

import grpc
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
    
    def get_max_short( self ):
        max_short = "000000"

        for string in self.get_conn_strings():
            conn = pg.connect( string )
            
            cur = conn.cursor()

            cur.execute(f"""
                select short
                from main.url
                order by short desc
                limit 1
            """)

            for row in cur.fetchall():
                if row[ 0 ] > max_short:
                    max_short = row[ 0 ]
            
            return max_short
    
    def get_max_id( self ):
        return base62.decode( self.get_max_short() )

    def __init__( self ):
        super().__init__()

        self.count = self.get_max_id()
    
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

    server.add_insecure_port( "[::]:50051" )
    
    server.start()
    
    server.wait_for_termination()

if __name__ == "__main__":
    serve()