from abc import ABC, abstractmethod

import redis.asyncio as aioredis
from .key_scheme import gen_key

class RedisPoolDao( ABC ):
    def __init__( self, redis: aioredis.Redis ):
        self.redis = redis

    @abstractmethod
    def get( self, short: str ):
        pass

    @abstractmethod
    def set( self, short: str, long: str ):
        pass