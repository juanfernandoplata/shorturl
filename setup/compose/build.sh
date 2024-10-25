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

echo 'services:' > ./docker-compose.yaml

pg_list=''
conn_strings=''

for (( i = 0; i < NUM_DBS; i++ )); do
    sed -e "s/_HOSTNAME/pg$i/" \
        -e "s/_IMG/$PREFIX-pg$i/" \
        -e "s/_CONT/$PREFIX-pg$i/" \
        ./templates/pg.yaml \
        >> ./docker-compose.yaml
    
    pg_list+="      - pg$i\n"
    conn_strings+="postgresql://pg:pg@pg$i:5432/shorturl,"
done

conn_strings=${conn_strings:0:-1}

api_list=''

echo "$conn_strings"

for (( i = 0; i < NUM_APIS; i++ )); do
    sed -e "s/_HOSTNAME/api$i/" \
        -e "s/_IMG/$PREFIX-api$i/" \
        -e "s/_CONT/$PREFIX-api$i/" \
        -e "s|_CONN_STRINGS|$conn_strings|" \
        -e "s/_DEPS_ON/$pg_list/" \
        ./templates/api.yaml \
        >> ./docker-compose.yaml

    api_list+="      - api$i\n"
done

sed -e "s/_HOSTNAME/back/" \
    -e "s/_IMG/$PREFIX-back/" \
    -e "s/_CONT/$PREFIX-back/" \
    -e "s/_DEPS_ON/$api_list/" \
    ./templates/back.yaml \
    >> ./docker-compose.yaml