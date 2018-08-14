#!/usr/bin/env bash

bin/minikube_kubectl.sh exec -it $(bin/minikube_get_pod.sh $1) -- ${@:2}
