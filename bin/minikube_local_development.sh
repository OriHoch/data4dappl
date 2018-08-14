#!/usr/bin/env bash

echo Modfying configuration file from pod, saving to ckan/development-local.ini

bin/minikube_kubectl.sh get secret etc-ckan-default -o json \
    | jq -r '.data["development.ini"]' \
    | base64 -d \
    | sed -e 's/redis:6379/localhost:6379/g' \
    | sed -e 's/solr:8983/localhost:8983/g' \
    | sed -e 's/db\/ckan/localhost\/ckan/g' \
    > ckan/development-local.ini
[ "$?" != "0" ] && echo failed to process configuration file && exit 1

echo Starting port forwards from minikube services to local ports: 6379, 8983, 5432

bin/minikube_port_forward.sh redis 6379 &
bin/minikube_port_forward.sh solr 8983 &
bin/minikube_port_forward.sh db 5432 &
wait
