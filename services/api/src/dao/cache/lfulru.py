from ..base import SUrlDao
from .base import Cache, CacheExp

from datetime import datetime

class LFULRUExp( CacheExp ):
    def __init__( self, tu = 1, lu = datetime.now() ):
        self._exp = ( tu, lu )
    
    def __lt__( self, other ):
        return self._exp < other._exp

    def __eq__( self, other ):
        return self._exp == other._exp
    
    def __repr__( self ):
        return self._exp.__repr__()

    def update( self ):
        times_used, _ = self._exp
        return LFULRUExp( times_used + 1, datetime.now() )

class LFULRUCache( Cache, SUrlDao ):
    def __init__( self, max_size = 5000 ):
        super().__init__( LFULRUExp, max_size )
    
    def set( self, key, value ):
        super().set( key, value, LFULRUExp() )
