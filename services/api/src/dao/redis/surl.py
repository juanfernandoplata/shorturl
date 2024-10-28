import redis.asyncio as aioredis

from .base import RedisPoolDao
from ..base import SUrlDao

from .key_scheme import gen_key

class RedisPoolSurlDao( RedisPoolDao, SUrlDao ):
    def __init__( self, redis: aioredis.Redis ):
        self.redis = redis

    def key_scheme( method ):
        def wrapper( * args, ** kwargs ):
            return method(
                args[ 0 ],
                gen_key( args[ 1 ] ),
                * args[ 2 : ],
                ** kwargs
            )
        
        return wrapper

    @key_scheme
    async def get( self, short: str ) -> str:
        return await self.redis.get( short )

    @key_scheme
    async def set( self, short: str, long: str ):
        await self.redis.set( short, long )
