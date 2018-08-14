#!/usr/bin/env bash

pipenv install &&\
pipenv run pip install -e 'git+https://github.com/OriHoch/ckan.git@ckan-2.7.2-fixing-odata-bug#egg=ckan' &&\
pipenv run pip install -e `pwd`/ckan/ckanext-odata_org_il
[ "$?" != "0" ] && echo installation failed && exit 1

echo Great Success
exit 0
