#!/usr/bin/env bash

# apply a job
# each job will run only once, to re-run, delete the job first: `kubectl delete job <job_name>`

set -e

if [ "${1}" == "" ]; then
    echo "usage: bin/k8s_apply_job.sh <job_name>"
else
    bin/k8s_connect.sh
    kubectl apply -f "k8s/jobs/${1}.yaml"
    sleep 5
    kubectl describe job "${1}"
    kubectl get pods
fi
