#!/usr/bin/env bash

set -e

wget -O- $1 -q | grep shopelectro.ru > /dev/null && echo "OK" || exit 1
