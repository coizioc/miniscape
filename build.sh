 GIT_HASH=$(git rev-parse --short HEAD)
 docker build -t miniscape-"$GIT_HASH" .