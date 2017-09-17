#!/usr/bin/env bash

# apply all configuration changes to the kubernetes cluster

set -e

if [ "${1}" == "" ]; then
    echo "usage: bin/k8s_apply.sh <deployment_name>"
else
    bin/k8s_connect.sh
    kubectl apply -f "k8s/${1}.yaml"
    kubectl rollout status "deployment/${1}"
    kubectl get pods
fi
