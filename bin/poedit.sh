#!/usr/bin/env bash

if ! which poedit; then
  sudo apt-get install poedit
fi

poedit ckan/ckanext-odata_org_il/ckanext/odata_org_il/i18n/he/LC_MESSAGES/ckan.po

