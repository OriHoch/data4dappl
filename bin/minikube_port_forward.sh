#!/usr/bin/env bash

bin/minikube_kubectl.sh port-forward $(bin/minikube_get_pod.sh $1) $2
