#!/usr/bin/env bash

set -e

CONTAINER_NAME=$1
CONTAINER_EXPECTED_STATE=$2
CONTAINER_STATE=

[[ $CONTAINER_NAME ]] || (echo "Specify a conatiner name as the first argument" && exit 1)
[[ $CONTAINER_EXPECTED_STATE ]] || (echo "Specify a container's expected state as the second argument" && exit 1)

function get-container-state() {
    sleep 1;
    CONTAINER_STATE=$(docker-compose ps | grep $CONTAINER_NAME | awk '{print $6}');
}

while [[ $CONTAINER_STATE != $CONTAINER_EXPECTED_STATE ]]; do get-container-state; done;
