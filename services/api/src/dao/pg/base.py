from sharding import PgShardManager

class PgShardDao():
    def __init__( self, shard_mannager: PgShardManager ):
        self.shard_mannager = shard_mannager