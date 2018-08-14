#!/usr/bin/env bash

bin/minikube_kubectl.sh get pods -l app=$1 -o 'jsonpath={.items[0].metadata.name}'