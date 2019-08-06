#!/usr/bin/env bash

pipenv install &&\
pipenv run pip install -e 'git+https://github.com/hasadna/ckan.git@2.8.1.9#egg=ckan' &&\
pipenv run pip install -e `pwd`/ckan/ckanext-odata_org_il &&\
pipenv run pip install -r ckan/requirements-odata.txt &&\
pipenv run pip install -r $(dirname `pipenv run which python`)/../src/ckan/hasadna-requirements.txt
[ "$?" != "0" ] && echo installation failed && exit 1

echo Great Success
exit 0
