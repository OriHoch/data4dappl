#!/usr/bin/env bash

if ! python --version 2>&1 | grep 'Python 2\.7\.'; then
    echo "WARNING! you might have an incompatible Python version"
fi

pip install -r ckan/requirement-setuptools.txt
pip install -r ckan/requirements-ckan.txt
if [ -f "${1:-/tmp}/ckan-2.7.2/setup.py" ]; then
    echo "Trying to install ckan from local copy at ${1:-/tmp}/ckan-2.7.2/setup.py"
    pip install -e "${1:-/tmp}/ckan-2.7.2"
else
    pip install -e 'git+https://github.com/OriHoch/ckan.git@ckan-2.7.2-fixing-odata-bug#egg=ckan'
fi
pip install -e ckan/ckanext-odata_org_il/
