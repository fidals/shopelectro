#!/usr/bin/env bash

# Copy the .dist environment files and wait them modifications.
# Merge them to .env file for docker-compose.

# Usage:
# `./create-env.sh`
# `./create-env.sh -q  # Quite mode`
# `./create-env.sh --quite  # Quite mode`

set -e

QUITE=false
for arg in "$@"
do
    if [[ $arg = "--quite" || $arg = "-q" ]]
    then
        QUITE=true
    fi
done


function join_by { local IFS="$1"; shift; echo "$*"; }

function create_env_files {
    new_files=()
    function new_file {
        file=$1
        new_file=${file%.dist}
        new_files+=( "$new_file" )

        if [[ ! -f "$new_file" ]]
        then
            cp $file $new_file
        fi
    }

    for file in env_files/*.dist
    do
        new_file $file
    done
    new_file ../shopelectro/settings/local.py.dist

    if ! $QUITE
    then
        file_names=$(join_by , ${new_files[@]})
        read -p \
"Checkout $file_names and configure it.
Are you ready to continue and build a new .env? [y/n]: " yn
        if [[ $yn != "y" ]]
        then
            # Give user possibility to refuse on .env generation,
            # but exit with zero code.
            # It's useful for `make deploy-dev`, for example.
            echo "Skip .env file creation"
            exit 0
        fi
    fi

    local env_doc=\
$'# Both .env and env_files/ are needed because of docker-compose realization.
# See good explanation here:
# https://github.com/docker/compose/issues/4223#issuecomment-280077263\n'
    echo "$env_doc" > .env

    for file in ${new_files[@]}
    do
        cat $file >> .env
    done
}

if ! $QUITE
then
    file_names=$(join_by , ${new_files[@]})
    read -p \
"Going to rewrite following all env and some django config files:
Continue? [y/n]: " yn
    if [[ $yn == "y" ]]
    then
        create_env_files
    fi
fi
exit 0
