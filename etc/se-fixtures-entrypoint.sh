#!/bin/env sh

# Compress actual database dump, compiled static files (js/css and some images)
# and mediafiles (whatever user uploads via admin panel or website)

for type in database media static
do
    echo $type
    tar -zcvf /opt/fixtures/$type.tar.gz -C /usr/app/src/$type .
done
