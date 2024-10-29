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

echo 'services:' > ./docker-compose.yaml

for (( i = 0; i < NUM_DBS; i++ )); do
    sed -e "s/\$SERV/pg$i/" \
        -e "s/\$IMG/$PREFIX-pg$i/" \
        -e "s/\$CONT/$PREFIX-pg$i/" \
        ./templates/pg.yaml \
        >> ./docker-compose.yaml
done

sed -e "s/\$SERV/redis/" \
    -e "s/\$IMG/$PREFIX-redis/" \
    -e "s/\$CONT/$PREFIX-redis/" \
    ./templates/redis.yaml \
    >> ./docker-compose.yaml

indent=$(get_indent './templates/api.yaml' '$DEPS')
pg_list=$(build_list './templates/api.yaml' '$DEPS' "${indent}- pg" '\n' 2 $NUM_DBS)

conn_strings=$(build_list './templates/api.yaml' '$CONNS' 'postgresql://pg:pg@pg' ':5432/shorturl,' 1 $NUM_DBS)

for (( i = 0; i < NUM_APIS; i++ )); do
    sed -e "s/\$SERV/api$i/" \
        -e "s/\$IMG/$PREFIX-api$i/" \
        -e "s/\$CONT/$PREFIX-api$i/" \
        -e "s|\$CONNS|$conn_strings|" \
        -e "s/^[ \s]*\$DEPS/$pg_list/" \
        ./templates/api.yaml \
        >> ./docker-compose.yaml
done

indent=$(get_indent './templates/nginx.yaml' '$DEPS')
api_list=$(build_list './templates/nginx.yaml' '$DEPS' "${indent}- pg" '\n' 2 $NUM_DBS)

sed -e "s/\$SERV/nginx/" \
    -e "s/\$IMG/$PREFIX-nginx/" \
    -e "s/\$CONT/$PREFIX-nginx/" \
    -e "s/^[ \s]*\$DEPS/$api_list/" \
    ./templates/nginx.yaml \
    >> ./docker-compose.yaml