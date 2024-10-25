create sequence shard_seq 
increment by 2
start with 1
minvalue 1;

create table url(
    url_id int default nextval( 'shard_seq' ) primary key,
    short varchar( 6 ) unique,
    long varchar( 256 )
);