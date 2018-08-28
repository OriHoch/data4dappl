#!/usr/bin/env bash

pipenv install &&\
pipenv run pip install -e 'git+https://github.com/hasadna/ckan.git@hasadna-ckan-2.8.1.0#egg=ckan' &&\
pipenv run pip install -e `pwd`/ckan/ckanext-odata_org_il
[ "$?" != "0" ] && echo installation failed && exit 1

echo Great Success
exit 0
