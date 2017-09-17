#!/usr/bin/env bash

bin/k8s_connect.sh

echo " > recreating secrets"

if [ -f k8s/secrets.env ] && ([ "${1}" == "" ] || [ "${1}" == "env-vars" ]); then
    kubectl delete secret env-vars
    kubectl create secret generic env-vars --from-env-file k8s/secrets.env
else
    echo "WARNING: skipping env-vars secret"
fi

if [ -d k8s/etc-ckan-default ] && ([ "${1}" == "" ] || [ "${1}" == "etc-ckan-default" ]); then
    kubectl delete secret etc-ckan-default
    kubectl create secret generic etc-ckan-default --from-file k8s/etc-ckan-default/
else
    echo "WARNING: skipping etc-ckan-default"
fi

kubectl describe secret env-vars
kubectl describe secret etc-ckan-default
