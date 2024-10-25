from abc import ABC, abstractmethod
from psycopg_pool import AsyncConnectionPool

class ShardKeyScheme( ABC ):
    @abstractmethod
    def find( self, key ):
        pass

    @abstractmethod
    def balance( self ):
        pass

class PgShardManager:
    def __init__( self, conn_dict, key_scheme: ShardKeyScheme ):
        self.conn_dict = conn_dict
        self.key_scheme = key_scheme
    
    async def open( self ):
        self.pools = dict()
        for key, string in self.conn_dict.items():
            self.pools[ key ] = AsyncConnectionPool( string, open = False )
            await self.pools[ key ].open()
    
    async def close( self ):
        for key, _ in self.conn_dict.items():
            await self.pools[ key ].close()

    def find( self, key, ret_db = False ):
        db = self.key_scheme.find( key )

        if ret_db:
            return db, self.pools[ db ].connection()

        return self.pools[ db ].connection()
    
    def balance( self, ret_db = False ):
        db = self.key_scheme.balance()

        if ret_db:
            return db, self.pools[ db ].connection()

        return self.pools[ db ].connection()
    
    def select( self, db ):
        return self.pools[ db ].connection()
