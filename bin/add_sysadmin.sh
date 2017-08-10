#!/usr/bin/env bash

if [ "${1}" == "" ]; then
    echo "usage: bin/add_sysadmin.sh <USER_NAME_TO_MAKE_ADMIN>"
else
    docker-compose run ckan sysadmin add $1 -c /etc/ckan/default/development.ini
fi
