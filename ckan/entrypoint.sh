#!/usr/bin/env bash

. ../../bin/activate

if [ "${1} ${2}" == "server start" ]; then
    ! pip install -e /ckanext-odata_org_il && echo failed to install extension && exit 1
    paster serve /etc/ckan/default/development.ini start &&\
    tail -f paster.log

elif [ "${1} ${2}" == "server restart" ]; then
    paster serve /etc/ckan/default/development.ini restart

elif [ "${1}" == "update-ckanext" ]; then
    rm -rf /data4dappl &&\
    git clone --depth 1 --single-branch --branch "${2:-master}" https://github.com/OriHoch/data4dappl.git /data4dappl &&\
    cp -rf /data4dappl/ckan/ckanext-odata_org_il/* /ckanext-odata_org_il/ &&\
    rm -rf /data4dappl &&\
    pip install -e /ckanext-odata_org_il &&\
    /entrypoint.sh server restart

else
    paster $*

fi
