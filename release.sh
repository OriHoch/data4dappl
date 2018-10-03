#!/usr/bin/env bash

DOCKER_DIR="${1}"
VERSION_LABEL="${2}"

[ "${VERSION_LABEL}" == "" ] \
    && echo ERROR! Missing version label \
    && echo current ${DOCKER_DIR}/VERSION.txt = $(cat ${DOCKER_DIR}/VERSION.txt) \
    && exit 1

docker build -t orihoch/data4dappl-${DOCKER_DIR}:v${VERSION_LABEL} ${DOCKER_DIR} &&\
docker push orihoch/data4dappl-${DOCKER_DIR}:v${VERSION_LABEL} &&\
echo "${VERSION_LABEL}" > ${DOCKER_DIR}/VERSION.txt &&\
echo orihoch/data4dappl-${DOCKER_DIR}:v${VERSION_LABEL} &&\
echo Great Success &&\
exit 0

exit 1
