from os import environ

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse

from sharding import PgShardManager, ShardKeyScheme

import redis.asyncio as aioredis

from dao.pg.surl import PgShardSurlDao
from dao.cache.lfulru import LFULRUCache
from dao.redis.surl import RedisPoolSurlDao

import base62

class ModShardKeyScheme( ShardKeyScheme ):
    def __init__( self, key_prefix, num_shards ):
        self.key_prefix = key_prefix
        self.num_shards = num_shards
        self.shard_sel = 0
    
    def find( self, key ):
        key = base62.decode( key )
        return f"{self.key_prefix}{key % self.num_shards}"

    def balance( self ):
        sel = self.shard_sel

        self.shard_sel = ( self.shard_sel + 1 ) % self.num_shards
        
        return f"{self.key_prefix}{sel}"

if ( HOSTNAME := environ.get( "HOSTNAME" ) ) == None:
    print( "FATAL: environment variable HOSTNAME was not found" )
    exit()

print( HOSTNAME )

HOSTNAME = "http://localhost"

shard_mannager = None
pg = None
redis = None
cache = None

app = FastAPI()

async def app_startup():
    global shard_mannager, pg, redis, cache

    if ( conn_strings := environ.get( "CONN_STRINGS" ) ) == None:
        print( "FATAL: environment variable CONN_STRINGS was not found" )
        exit()
    
    conn_strings = conn_strings.split( "," )
    
    shards_keys = [ f"pg{i}" for i in range( len( conn_strings ) ) ]

    conn_dict = dict( zip(
        shards_keys,
        conn_strings
    ))

    shard_mannager = PgShardManager(
        conn_dict,
        ModShardKeyScheme( "pg", len( shards_keys ) )
    )

    await shard_mannager.open()

    pg = PgShardSurlDao( shard_mannager )

    redis_pool = aioredis.ConnectionPool.from_url(
        "redis://surl-redis:6379", # TAKW THIS TO AN ENVIRON!!!
        max_connections = 10
    )

    redis = RedisPoolSurlDao( aioredis.Redis( connection_pool = redis_pool ) )

    cache = LFULRUCache( max_size = 3 )

async def app_shutdown():
    await shard_mannager.close()

@asynccontextmanager
async def lifespan( app ):
    await app_startup()
    yield
    await app_shutdown()

app = FastAPI( lifespan = lifespan )

@app.post( "/generate" )
async def search( long: str, bg: BackgroundTasks ):
    short = await pg.reserve( long )

    bg.add_task( pg.set, short, long )

    return { "short": f"{HOSTNAME}/{short}" }

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