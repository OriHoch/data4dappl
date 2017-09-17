#!/usr/bin/env bash

# switch to the correct kubernetes cluster - be sure to run this before any other k8s command

set -e

if ! kubectl config use-context gke_hasadna-odata_us-central1-a_data4dappl; then
    gcloud container clusters get-credentials \
        data4dappl \
        --zone us-central1-a \
        --project hasadna-odata
fi
