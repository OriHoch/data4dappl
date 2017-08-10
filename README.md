# data4dappl

## Quickstart

This will setup a local ckan instance, including the odata extension and all needed depdencies (solr, db, redis)

* Install latest version of docker and docker-compose
* `bin/start.sh`
* `bin/initialize_db.sh`

## Installing the ckan extension on an existing ckan project

If you have an existing ckan installation and just want to install the odata plugin:

* Install the package (should run inside your ckan installations virtualenv):
  * `pip install -e 'git+https://github.com/OriHoch/data4dappl.git#egg=ckanext-odata_org_il&subdirectory=ckan/ckanext-odata_org_il'`
* Edit the configuration (E.g. /etc/ckan/default/development.ini)
  * add odata_org_il to ckan.plugins
* restart ckan
