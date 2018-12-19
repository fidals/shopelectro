#!/bin/env sh

# Compress actual database dump, compiled static files (js/css and some images)
# and mediafiles (whatever user uploads via admin panel or website)

for type in database media static
do
    tar -zcvf /opt/backup/$type-`date "+%Y-%m-%d"`.tar.gz -C /usr/app/src/$type .
done

# delete files older than DAYS_TO_STORE days
find /opt/backup/* -mtime +${DAYS_TO_STORE:-7} -print -delete
