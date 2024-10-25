#!/bin/bash

if [ $# -ne 3 ]; then
    usage="Usage: build.sh <prefix> <num_dbs> <num_apis>\n"
    usage="$usage\n  prefix: Prefix for image tags\n"
    usage="$usage\n  num_dbs: Number of DBs to spawn\n"
    usage="$usage\n  num_apis: Number of APIs to spawn\n\n"

    echo -e "$usage"

    exit 1
fi

PREFIX=$1
NUM_DBS=$2
NUM_APIS=$3

for (( i = 0; i < NUM_DBS; i++ )); do
    sed -e "s/_INCR/$NUM_DBS/" \
        -e "s/_START/$i/" \
        ../../services/postgres/_init.sql \
        > ../../services/postgres/init.sql
    
    docker build -t "$PREFIX-pg$i" ../../services/postgres/
done

apis=''

for (( i = 0; i < NUM_APIS; i++ )); do
    docker build -t "$PREFIX-api$i" ../../services/api/

    apis+="        server api$i:80;\n"
done

sed -e "s/_APIS/$apis/" ../../services/back/_nginx.conf > ../../services/back/nginx.conf

docker build -t "$PREFIX-back" ../../services/back/