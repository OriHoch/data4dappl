#!/usr/bin/env bash

DEPLOYMENT_NAME="${1}"
IMAGE="${2}"
CONTAINER_NAME="${3:-$DEPLOYMENT_NAME}"
APP_LABEL="${4:-$DEPLOYMENT_NAME}"

echo sending docker image ${IMAGE} to minikube

! docker save "${IMAGE}" | (eval $(minikube docker-env) && docker load) \
    && echo failed to send image to minikube && exit 1

echo patching deployment ${DEPLOYMENT_NAME} with image ${IMAGE}

PATCH='{"spec": {
    "template": {
        "metadata": {
            "labels": {
                "app": "'${APP_LABEL}'",
                "date": "'`date +%s`'"
            }
        },
        "spec": {
            "containers": [
                {"name": "'${CONTAINER_NAME}'", "image": "'${IMAGE}'"}
            ]
        }
    }
}}'

bin/minikube_kubectl.sh patch deployment "${DEPLOYMENT_NAME}" -p $(echo $PATCH | jq . -Mc) &&\
bin/minikube_kubectl.sh rollout status deployment "${DEPLOYMENT_NAME}"
[ "$?" != "0" ] && echo deployment failed && exit 1

echo Great Success
exit 0
