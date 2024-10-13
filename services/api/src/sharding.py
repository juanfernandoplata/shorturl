from psycopg_pool import AsyncConnectionPool

class PgShardManager:
    def __init__( self, conn_dict, shard_selector ):
        self.conn_dict = conn_dict
        self.shard_selector = shard_selector
    
    async def open( self ):
        self.pools = dict()

        for key, string in self.conn_dict.items():
            self.pools[ key ] = AsyncConnectionPool( string, open = False )
            await self.pools[ key ].open()
    
    async def close( self ):
        for key, _ in self.conn_dict.items():
            await self.pools[ key ].close()

    def connection( self, key ):
        return self.pools[ self.shard_selector( key ) ].connection()