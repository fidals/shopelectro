#!/usr/bin/env bash

alias dc=docker-compose

dc run --rm app python manage.py makemessages --ignore 'venv/**'
read -n1 -p "I18n messages generated. Are you ready to compile them [y/n]: " yn
echo ""  # new line
if [[ $yn == "y" ]]
then
  docker-compose run --rm app python manage.py compilemessages -l ru
else
  echo "Skip messages compilation"
fi
exit 0
