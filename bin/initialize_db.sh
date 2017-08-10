#!/usr/bin/env bash

docker-compose run ckan db init -c /etc/ckan/default/development.ini
