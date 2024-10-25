from os import environ

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse

from sharding import PgShardManager

from cache import LFULRUCache

import base62

if ( HOSTNAME := environ.get( "HOSTNAME" ) ) == None:
    print( "FATAL: environment variable HOSTNAME was not found" )
    exit()

HOSTNAME = "http://localhost"

dbs = None
cache = None
app = FastAPI()

async def app_startup():
    global dbs, cache

    if ( conn_strings := environ.get( "CONN_STRINGS" ) ) == None:
        print( "FATAL: environment variable CONN_STRINGS was not found" )
        exit()
    
    conn_strings = conn_strings.split( "," )
    
    shards_keys = [ f"pg{i}" for i in range( len( conn_strings ) ) ]

    conn_dict = dict( zip(
        shards_keys,
        conn_strings
    ))

    dbs = PgShardManager(
        conn_dict,
        ModShardKeyScheme( "pg", len( shards_keys ) )
    )

    await dbs.open()

    cache = LFULRUCache( max_size = 3 )

async def app_shutdown():
    await dbs.close()

@asynccontextmanager
async def lifespan( app ):
    await app_startup()
    yield
    await app_shutdown()

app = FastAPI( lifespan = lifespan )

async def set_short_long( db, url_id, short, long ):
    async with dbs.select( db ) as conn:
        await conn.execute( f"""
            update url set
            short = '{short}',
            long = '{long}'
            where url_id = {url_id}
        """ )

@app.post( "/generate" )
async def search( url: str, bg: BackgroundTasks ):
    db, connection = dbs.balance( ret_db = True )

    async with connection as conn:
        curr = await conn.execute( f"""
            insert into url default values
            returning url_id
        """ )

        url_id = ( await curr.fetchone() )[ 0 ]

        short = base62.encode( url_id )

        bg.add_task( set_short_long, db, url_id, short, url )

    return { "short": f"{HOSTNAME}/{short}" }

@app.get( "/{short}" )
async def search( short: str, bg: BackgroundTasks ):
    if ( long := cache.get( short ) ):
        print( "CACHE HIT" )
        return RedirectResponse( long )
    
    print( "CACHE MISS" )

    async with dbs.find( short ) as conn:
        curr = await conn.execute( f"""
            select long
            from url
            where short = '{short}'
        """ )

        if ( long := ( await curr.fetchone() ) ) == None:
            raise HTTPException(
                status_code = 404,
                detail = "URL was not found"
            )
        
        long = long[ 0 ]

        # Launch bg task for metrics micro-service
    
    cache.set( short, long )

    return RedirectResponse( long )