#!/usr/bin/env bash

pipenv install &&\
pipenv run pip install -e 'git+https://github.com/hasadna/ckan.git@hasadna-ckan-2.8.1.3#egg=ckan' &&\
pipenv run pip install -e `pwd`/ckan/ckanext-odata_org_il
pipenv run pip install -r ckan/requirements-odata.txt
[ "$?" != "0" ] && echo installation failed && exit 1

echo Great Success
exit 0
