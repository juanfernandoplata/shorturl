from abc import ABC, abstractmethod

class SUrlDao( ABC ):
    @abstractmethod
    def get( self, short: str ) -> str:
        pass

    @abstractmethod
    def set( self, short: str, long: str ):
        pass