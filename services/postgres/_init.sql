create sequence shard_seq 
increment by _INCR
start with _START
minvalue _START;

create table url(
    url_id int default nextval( 'shard_seq' ) primary key,
    short varchar( 6 ) unique,
    long varchar( 256 )
);