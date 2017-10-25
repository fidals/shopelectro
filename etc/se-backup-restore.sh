#!/bin/env sh

sudo mkdir -p /opt/backup/shopelectro/
sudo chown -R `whoami` /opt/

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
