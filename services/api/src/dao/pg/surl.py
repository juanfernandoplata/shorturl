from .base import PgShardDao
from ..base import SUrlDao

from sharding import PgShardManager

import base62

class PgShardSurlDao( PgShardDao, SUrlDao ):
    def __init__( self, shard_mannager: PgShardManager ):
        super().__init__( shard_mannager )
        self.to_set = dict()

    async def reserve( self, long: str ) -> str:
        db = None
        url_id = None
        short = None

        db, connection = self.shard_mannager.balance( ret_db = True )

        async with connection as conn:
            curr = await conn.execute( f"""
                insert into url( long )
                values( '{ long }' )
                returning url_id
            """ )

            url_id = ( await curr.fetchone() )[ 0 ]

            short = base62.encode( url_id )
        
        self.to_set[ short ] = ( db, url_id )
    
        return short

    async def get( self, short: str ) -> str:
        async with self.shard_mannager.find( short ) as conn:
            curr = await conn.execute( f"""
                select long
                from url
                where short = '{ short }'
            """ )

            if ( long := ( await curr.fetchone() ) ) == None:
                return None
            
            return long[ 0 ]

    async def set( self, short: str, long: str ):
        if ( aux := self.to_set[ short ] ) == None:
            print( "FATAL: this sould never print!!!" )
            exit()
        
        db, url_id = aux

        async with self.shard_mannager.select( db ) as conn:
            await conn.execute( f"""
                update url set
                short = '{ short }'
                where url_id = { url_id }
            """ )