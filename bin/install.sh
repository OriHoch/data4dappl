#!/usr/bin/env bash

if ! python --version 2>&1 | grep 'Python 2\.7\.'; then
    echo "WARNING! you might have an incompatible Python version"
fi

pip install -r ckan/requirement-setuptools.txt
pip install -r ckan/requirements-ckan.txt
pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.7.0#egg=ckan'
pip install -e ckan/ckanext-odata_org_il/
