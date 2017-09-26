#!/usr/bin/env bash

if [ ! -f ckan-dump/data.tar.gz ] || [ ! -f ckan-dump/db.gz ]; then
    echo "ERROR! missing ckan-dump/ files"
    echo "see how to create it in k8s/README.md"
    exit 1
fi

docker cp ckan-dump/db.gz data4dappl_ckan_1:/db.gz
docker-compose exec ckan bash -c "
    gunzip -c /db.gz > /db &&
    ../../bin/paster --plugin=ckan db clean -c /etc/ckan/default/development.ini &&
    ../../bin/paster --plugin=ckan db load /db -c /etc/ckan/default/development.ini
"
