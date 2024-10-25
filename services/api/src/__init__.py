from sharding import ShardKeyScheme
import base62

class ModShardKeyScheme( ShardKeyScheme ):
    def __init__( self, key_prefix, num_shards ):
        self.key_prefix = key_prefix
        self.num_shards = num_shards
        self.shard_sel = 0
    
    def find( self, key ):
        key = base62.decode( key )
        return f"{self.key_prefix}{key % self.num_shards}"

    def balance( self ):
        sel = self.shard_sel

        self.shard_sel = ( self.shard_sel + 1 ) % self.num_shards
        
        return f"{self.key_prefix}{sel}"