#!/bin/bash

if [ $# -ne 3 ]; then
    usage="Usage: build.sh <prefix> <num_dbs> <num_apis>\n"
    usage="$usage\n  prefix: Prefix for image tags\n"
    usage="$usage\n  num_dbs: Number of DBs to spawn\n"
    usage="$usage\n  num_apis: Number of APIs to spawn\n\n"

    echo -e "$usage"

    exit 1
fi

get_indent() {
    file=$1
    var=$2

    indent=$(grep -o "^[ \s]*$var" "$file")

    i=$((${#indent} - ${#var}))
    
    indent=${indent::i}

    echo "$indent"
}

build_list() {
    file=$1
    var=$2
    prefix=$3
    suffix=$4
    rm=$5
    n=$6

    list=''

    for (( i = 0; i < $n; i++ )); do
        list+="$prefix$i$suffix"
    done

    if [ $rm -ne 0 ]; then
        list=${list::-$rm}
    fi

    echo "$list"
}

PREFIX=$1
NUM_DBS=$2
NUM_APIS=$3

for (( i = 0; i < NUM_DBS; i++ )); do
    sed -e "s/\$INCR/$NUM_DBS/" \
        -e "s/\$START/$i/" \
        ../../services/postgres/_init.sql \
        > ../../services/postgres/init.sql
    
    docker build -t "$PREFIX-pg$i" ../../services/postgres/
done

rm ../../services/postgres/init.sql

indent=$(get_indent '../../services/nginx/_nginx.conf' '$APIS')
apis=$(build_list '../../services/nginx/_nginx.conf' '$APIS' "${indent}server api" ':80;\n' 2 $NUM_APIS)

docker build -t "$PREFIX-redis" ../../services/redis/

for (( i = 0; i < NUM_APIS; i++ )); do    
    docker build -t "$PREFIX-api$i" ../../services/api/
done

sed -e "s/^[ \s]*\$APIS/$apis/" ../../services/nginx/_nginx.conf > ../../services/nginx/nginx.conf

docker build -t "$PREFIX-nginx" ../../services/nginx/

rm ../../services/nginx/nginx.conf