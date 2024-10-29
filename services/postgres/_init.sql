create sequence shard_seq 
increment by $INCR
start with $START
minvalue $START;

create table url(
    url_id int default nextval( 'shard_seq' ) primary key,
    short varchar( 6 ) unique,
    long varchar( 256 )
);