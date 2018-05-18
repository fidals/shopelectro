#!/bin/env sh

sudo mkdir -p /opt/backup/shopelectro/
sudo chown -R `whoami` /opt/

# @todo #232 - DB restore error on local env.
#  How to reproduce:
#  - launch this script
#  - restart se-python container
#
#  Traceback message:
#  ```
#  django.db.utils.OperationalError: FATAL:  could not open relation mapping file "global/pg_filenode.map": Permission denied
#  ```

for type in database media static
do
    while true; do
        read -p "Do you wish to download $type [y/n]: " yn
        case $yn in
            [Yy]* ) echo "Downloading $type...";
                    scp root@shopelectro.ru:/opt/backup/shopelectro/$type.tar.gz /opt/backup/shopelectro/$type.tar.gz;
                    mkdir -p /opt/$type/shopelectro;
                    tar xvfz /opt/backup/shopelectro/$type.tar.gz --directory /opt/$type/shopelectro;
                    break;;
            [Nn]* ) break;;
            * ) echo "Please answer yes or no.";;
        esac
    done
done
