#!/usr/bin/env bash

if ! [ -e ckan/development-local.ini ]; then
    echo Modfying configuration file from pod, saving to ckan/development-local.ini
    CKAN_POD_NAME=$(kubectl get pods -l app=ckan -o 'jsonpath={.items[0].metadata.name}')
    kubectl exec -it $CKAN_POD_NAME cat /etc/ckan/production.ini \
        | sed -e 's/redis:6379/localhost:6379/g' \
        | sed -e 's/solr:8983/localhost:8983/g' \
        | sed -e 's/db\/ckan/localhost\/ckan/g' \
        | sed -e 's/ckan-jobs-db\/postgres/localhost:5433\/postgres/g' \
        | sed -e 's/datastore-db\/datastore/localhost:5434\/datastore/g' \
        > ckan/development-local.ini
    [ "$?" != "0" ] && echo failed to process configuration file && exit 1
fi

echo Starting port forwards from minikube services to local ports: 6379, 8983, 5432

bin/minikube_port_forward.sh redis 6379 &
bin/minikube_port_forward.sh solr 8983 &
bin/minikube_port_forward.sh db 5432 &
bin/minikube_port_forward.sh ckan-jobs-db 5433:5432 &
bin/minikube_port_forward.sh datastore-db 5434:5432 &
wait
