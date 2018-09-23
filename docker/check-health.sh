#!/usr/bin/env sh

URL=$1

if [ -z $URL ]
then
    echo "Specify an url to be checked as the first argument"
    exit 1
fi

wget -O- $URL -q | grep shopelectro.ru > /dev/null && echo "OK" || exit 1
