from os import environ

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse

from logging import getLogger

from contextlib import asynccontextmanager

from sharding import PgShardManager
from __init__ import ModShardKeyScheme

import redis.asyncio as aioredis

from dao.pg.surl import PgShardSurlDao
from dao.cache.lfulru import LFULRUCache
from dao.redis.surl import RedisPoolSurlDao

logger = getLogger( "uvicorn.error" )

if ( DHOSTNAME := environ.get( "DHOSTNAME" ) ) == None:
    logger.error( "(FATAL) Environment variable HOSTNAME was not found" )
    exit()

if ( PGS := environ.get( "PGS" ) ) == None:
    logger.error( "(FATAL) Environment variable PGS was not found" )
    exit()

if ( PG_PSIZE := environ.get( "PG_PSIZE" ) ) == None:
    PG_PSIZE = 10
else:
    PG_PSIZE = int( PG_PSIZE )

if ( REDIS := environ.get( "REDIS" ) ) == None:
    logger.error( "(FATAL) Environment variable REDIS was not found" )
    exit()

if ( REDIS_PSIZE := environ.get( "REDIS_PSIZE" ) ) == None:
    REDIS_PSIZE = 10
else:
    REDIS_PSIZE = int( REDIS_PSIZE )

if ( CACHE_SIZE := environ.get( "CACHE_SIZE" ) ) == None:
    CACHE_SIZE = 5000
else:
    CACHE_SIZE = int( CACHE_SIZE )

shard_mannager = None
pg = None
redis = None
cache = None

async def app_startup():
    global shard_mannager, pg, redis, cache
    
    conn_urls = PGS.split( "," )
    
    shards_keys = [ f"pg{i}" for i in range( len( conn_urls ) ) ]

    conn_dict = dict( zip(
        shards_keys,
        conn_urls
    ))

    shard_mannager = PgShardManager(
        conn_dict,
        ModShardKeyScheme( "pg", len( shards_keys ) )
    )

    await shard_mannager.open( pool_size = PG_PSIZE )

    pg = PgShardSurlDao( shard_mannager )

    redis_pool = aioredis.ConnectionPool.from_url(
        REDIS,
        max_connections = REDIS_PSIZE
    )

    redis = RedisPoolSurlDao( aioredis.Redis( connection_pool = redis_pool ) )

    cache = LFULRUCache( max_size = CACHE_SIZE )

async def app_shutdown():
    await shard_mannager.close()

@asynccontextmanager
async def lifespan( app: FastAPI ):
    await app_startup()
    yield
    await app_shutdown()

app = FastAPI( lifespan = lifespan )

@app.post( "/generate" )
async def search( long: str, bg: BackgroundTasks ):
    short = await pg.reserve( long )

    bg.add_task( pg.set, short, long )

    return { "short": f"{DHOSTNAME}/{short}" }

@app.get( "/{short}" )
async def search( short: str, bg: BackgroundTasks ):
    if ( long := cache.get( short ) ):
        return RedirectResponse( long )
    
    if ( long := await redis.get( short ) ):
        return RedirectResponse( long )
        
    if ( long := await pg.get( short ) ) == None:
        raise HTTPException(
            status_code = 404,
            detail = "URL was not found"
        )

    # Launch bg task for metrics micro-service
    
    cache.set( short, long )

    return RedirectResponse( long )