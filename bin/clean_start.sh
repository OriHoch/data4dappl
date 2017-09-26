#!/usr/bin/env bash

docker-compose down -v
bin/recreate_templates.sh
docker-compose up -d --build
bin/load_ckan_dump.sh
docker-compose restart ckan
