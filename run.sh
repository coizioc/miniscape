GIT_HASH=$(git rev-parse --short HEAD)
docker run \
    -v $(pwd)/config.py:/opt/miniscape/config.py \
    -v $(pwd)/db.sqlite3:/opt/miniscape/db.sqlite3 \
    -v $(pwd)/resources:/opt/miniscape/resources \
    miniscape-"$GIT_HASH"