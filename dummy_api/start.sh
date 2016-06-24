#!/bin/bash
set -ev

docker run -p 8282:8080 --name core -d eregs/core
# Sleep for 5 to give Django enough time to start up
sleep 5

# Load dummy data (@todo - replace with real data)
for TAIL in $(find */* -type f | sort -r)
do
    curl -X PUT http://localhost:8282/$TAIL -d @$TAIL
done

mkdir cache
# Load a real reg
docker run --rm -it -v $PWD/cache:/app/cache --link core:core eregs/parser pipeline 12 1005 http://core:8080 --only-latest

# Load a real notice
docker run --rm -it -v $PWD/cache:/app/cache eregs/parser notice_preamble 2016-02749
docker run --rm -it -v $PWD/cache:/app/cache eregs/parser layers
docker run --rm -it -v $PWD/cache:/app/cache --link core:core eregs/parser write_to http://core:8080

# Modify the close date
curl http://localhost:8282/notice/2016-02749 | python -m json.tool > notice.json
FUTURE=`date --date="1 month" +"%Y-%m-%d"`
sed -i "s/2016-04-29/$FUTURE/g" notice.json
curl -X PUT http://localhost:8282/notice/2016-02749 -d @notice.json

docker logs core
