from abc import ABC, abstractmethod

import heapq

class CacheExp( ABC ):
    @abstractmethod
    def __lt__( self, other ):
        pass
    
    @abstractmethod
    def __eq__( self, other ):
        pass

    @abstractmethod
    def update( self, exp ):
        pass

class Cache:
    def __init__(
        self,
        CacheExpClass: CacheExp,
        max_size = 5000
    ):
        self._RecordClass = CacheExpClass

        self._max_size = max_size
        
        self._exp = list()
        self._cache = dict()
    
    def __repr__( self ):
        repr = "CACHE\n"

        for r in self._cache:
            repr += f"{r} --> {self._cache[ r ].__repr__()}\n"

        return repr
    
    def apply_policy( self ):
        exp, key = heapq.heappop( self._exp )

        while self._cache[ key ][ 1 ] != exp:
            exp, key = heapq.heappop( self._exp )

        self._cache.pop( key )
    
    def set( self, key, value, exp ):
        assert isinstance( exp, self._RecordClass )
        
        if self._cache.get( key, None ) == None:
            if len( self._cache ) == self._max_size:
                self.apply_policy()
        
        heapq.heappush( self._exp, ( exp, key ) )
        self._cache[ key ] = ( value, exp )
    
    def get( self, key ):
        if ( entry := self._cache.get( key, None ) ) == None:
            return None

        value, exp = entry

        exp = exp.update()

        heapq.heappush( self._exp, ( exp, key ) )
        self._cache[ key ] = ( value, exp )

        return value
