#!/usr/bin/env bash

CKAN_TAG="ckan-2.8.1"

curl -L https://github.com/ckan/ckan/raw/${CKAN_TAG}/requirement-setuptools.txt > ckan/requirement-setuptools.txt &&\
curl -L https://github.com/ckan/ckan/raw/${CKAN_TAG}/requirements.txt > ckan/requirements-ckan.txt &&\
curl -L https://github.com/ckan/ckan/raw/${CKAN_TAG}/ckan/config/solr/schema.xml > solr/schema.xml
