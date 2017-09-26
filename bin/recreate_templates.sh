#!/usr/bin/env bash

echo " > generating ckan configurations (development.ini / who.ini) for local development using the docker compose environment"

export CKAN_BEAKER_SESSION_SECRET="j7ENvb8zg5N2Ynk4c0GoXVmqL"
export CKAN_APP_INSTANCE_UUID="cab7d4cf-03bf-4a81-b6ca-cb52c1b842ce"
export CKAN_SQLALCHEMY_URL="postgresql://postgres:123456@db/postgres"
export CKAN_SITE_URL="http://localhost:5000"
export CKAN_SOLR_URL="http://solr:8983/solr/"
export CKAN_REDIS_URL="redis://redis:6379/0"
export CKAN_STORAGE_PATH="/var/lib/ckan/data"
export CKAN_MAX_RESOURCE_SIZE="500"
export CKAN_DEBUG=false

export COMMENT="default ckan configuration for local development - connects with the docker compose environment services"
bin/templater.sh ckan/development.ini.template > ckan/development.ini

export COMMENT="who.ini ckan configuration for local development"
bin/templater.sh ckan/who.ini.template > ckan/who.ini

echo " > generating ckan configurations for connecting to docker services from local ckan"

export CKAN_SQLALCHEMY_URL="postgresql://postgres:123456@localhost:15432/postgres"
export CKAN_SITE_URL="http://localhost:5000"
export CKAN_SOLR_URL="http://localhost:18983/solr/"
export CKAN_REDIS_URL="redis://localhost:16379/0"
export CKAN_STORAGE_PATH="/var/lib/ckan/data"
export CKAN_MAX_RESOURCE_SIZE="500"
export CKAN_DEBUG=false

export COMMENT="ckan configuration for connectin to docker service from local ckan"
bin/templater.sh ckan/development.ini.template > ckan/development-local.ini

exit 0
