#!/usr/bin/env bash

set -e

URL=$1
[[ $URL ]] || (echo "Specify an url to be checked as the first argument" && exit 1)

wget -O- $URL -q | grep shopelectro.ru > /dev/null && echo "OK" || exit 1
