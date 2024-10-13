import psycopg as pg

class PgShardManager:
    def __init__( self, conn_dict, shard_selector ):
        self.conn_dit = conn_dict
        self.shard_selector = shard_selector
    
    async def open( self ):
        self.pools = dict()

        for key, string in self.conn_dict:
            self.pools[ key ] = pg.AsyncConnectionPool( string, open = False )
            await self.pools[ key ].open()


    async def connection( self, key ):
        return self.pools[ self.shard_selector( key ) ].connection()