from os import environ

from contextlib import asynccontextmanager

from fastapi import FastAPI

from sharding import PgShardManager

import grpc
from _grpc.url_encoder_pb2_grpc import UrlEncoderStub
from _grpc.url_encoder_pb2 import EncodeReq

from _grpc import tsl

dbs = None

channel = None
encoder = None

app = FastAPI()

async def app_startup():
    global dbs, channel, encoder

    if ( conn_strings := environ.get( "CONN_STRINGS" ) ) == None:
        print( "FATAL: environment variable CONN_STRINGS was not found" )
        exit()
    
    conn_strings = conn_strings.split( "," )
    
    conn_dict = dict( zip(
        [ f"pg{i}" for i in range( 1, len( conn_strings ) + 1 ) ],
        conn_strings
    ))

    dbs = PgShardManager(
        conn_dict,
        lambda key: "pg1" if ord( key[ -1 ] ) < 86 else "pg2"
    )

    credentials = grpc.ssl_channel_credentials(
        root_certificates = tsl.ROOT_CERTIFICATES,
        certificate_chain = tsl.CLIENT_CERTIFICATE,
        private_key = tsl.CLIENT_KEY,
    )

    channel = grpc.secure_channel( "url-encoder:50051", credentials )

    encoder = UrlEncoderStub( channel )

    await dbs.open()

async def app_shutdown():
    await dbs.close()
    channel.close()

@asynccontextmanager
async def lifespan( app ):
    await app_startup()
    yield
    await app_shutdown()

app = FastAPI( lifespan = lifespan )

@app.post( "/generate" )
async def search( url: str ):
    encoded = encoder.encode( EncodeReq() ).encoded

    async with dbs.connection( encoded ) as conn:
        await conn.execute( f"""
            insert into url values('{encoded}')
        """ )

    return { "short": encoded }