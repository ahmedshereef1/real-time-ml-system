#!/bin/bash

# Builds a docker image for the given dockerfile and pushes it to the docker registry
# given by the env variable

set -e

image_name=$1
env=$2

# Just checking that the user has provided the correct number of arguments
if [ -z "$image_name" ]; then
    echo "Usage: $0 <image_name> <env>"
    exit 1
fi

if [ -z "$env" ]; then
    echo "Usage: $0 <image_name> <env>"
    exit 1
fi

# check that env is either "dev" or "prod"
if [ "$env" != "dev" ] && [ "$env" != "prod" ]; then
    echo "env must be either dev or prod"
    exit 1
fi

if [ "$env" == "dev" ]; then
    echo "Building image ${image_name} for dev"
    docker build -t ${image_name}:dev -f docker/${image_name}.Dockerfile .
    kind load docker-image ${image_name}:dev --name rwml-34fa
else
    echo "Building image ${image_name} for prod"

    BUILD_DATE=$(date +%s)
    GIT_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    BUILD_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    REPO_URL="https://github.com/ahmedshereef1/real-time-ml-system"

    docker buildx build --push \
        --platform linux/amd64 \
        -t ghcr.io/ahmedshereef1/${image_name}:0.1.5-beta.${BUILD_DATE} \
        --label org.opencontainers.image.revision=${GIT_COMMIT} \
        --label org.opencontainers.image.created=${BUILD_TIME} \
        --label org.opencontainers.image.source="${REPO_URL}" \
        --label org.opencontainers.image.url="${REPO_URL}/docker/${image_name}.Dockerfile" \
        --label org.opencontainers.image.title="${image_name}" \
        --label org.opencontainers.image.description="${image_name} Dockerfile" \
        -f docker/${image_name}.Dockerfile .
fi



