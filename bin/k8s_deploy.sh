#!/usr/bin/env bash

set -e

bin/k8s_apply.sh redis
sleep 1
bin/k8s_apply.sh db
sleep 5
bin/k8s_apply.sh solr
sleep 5
bin/k8s_apply.sh ckan
sleep 5
bin/k8s_apply.sh adminer
