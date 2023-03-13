#!/usr/bin/env bash

# Set the container name to the name of the current GitHub repository
container_name="${GITHUB_REPOSITORY##*/}"

# Set the container version to the current UTC time and
# the first 7 characters of the Git commit hash
build_date=$(date -u +"%F_%H-%M")
commit_hash="${GITHUB_SHA::7}"
container_version="${build_date}_${commit_hash}"

# Output the Docker container tag using the registry name, container name,
# and container version
echo "registry.digitalocean.com/$REGISTRY/$container_name:$container_version"
