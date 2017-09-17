#!/usr/bin/env bash

function get_pod_names() {
    for n in $1; do kubectl get pods -n $n | tail -n +2; done | cut -d " " -f 1
}

if [ "${1}" == "" ]; then
    echo "usage: bin/k8s_get_pod_names.sh <namespace/s> [name_starts_with]"
else
    bin/k8s_connect.sh >&2
    if [ "${2}" == "" ]; then
        get_pod_names "${1}"
    else
        get_pod_names $1 | grep "^${2}"
    fi
fi
