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
    docker rmi "$PREFIX-pg$i"
done

for (( i = 0; i < NUM_APIS; i++ )); do
    docker rmi "$PREFIX-api$i"
done

docker rmi "$PREFIX-back"