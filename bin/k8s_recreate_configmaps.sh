#!/usr/bin/env bash

bin/k8s_connect.sh

echo " > recreating configmaps"

kubectl delete configmap nginx-conf-d
kubectl create configmap nginx-conf-d --from-file k8s/nginx-conf-d/
kubectl describe configmap nginx-conf-d
