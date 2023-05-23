#!/bin/bash
# args:
# $1 : marqo_image_name - name of the image you want to test
# $2 : env_vars - string representing the env vars to pass marqo
set -x
docker rm -f marqo;

MARQO_DOCKER_IMAGE="$1"
shift

docker run -d --name marqo --gpus all --privileged -p 8882:8882 --add-host host.docker.internal:host-gateway ${@:+"$@"} "$MARQO_DOCKER_IMAGE"

# Follow the logs of the Docker container in the background and capture its PID
docker logs -f marqo &
LOGS_PID=$!

# wait for marqo to start
set +x
until [[ $(curl -v --silent --insecure http://localhost:8882 2>&1 | grep Marqo) ]]; do
    sleep 0.1;
done;
set -x
# Kill the `docker logs` command (so subprocess does not wait for it)
kill $LOGS_PID
set +x