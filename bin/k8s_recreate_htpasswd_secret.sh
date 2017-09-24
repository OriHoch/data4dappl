#!/usr/bin/env bash

bin/k8s_connect.sh

echo " > recreating htpasswd secret"

TEMPDIR=`mktemp -d`
htpasswd -c "${TEMPDIR}/htpasswd" superadmin
kubectl delete secret nginx-htpasswd
kubectl create secret generic nginx-htpasswd --from-file "${TEMPDIR}/"
kubectl describe secret nginx-htpasswd
rm -rf $TEMPDIR
