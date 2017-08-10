#!/usr/bin/env bash

. ../../bin/activate

pip install -e /ckanext-odata_org_il

paster $*
