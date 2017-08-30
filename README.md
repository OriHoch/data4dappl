# data4dappl

## Quickstart

This will setup a local ckan instance, including the odata extension and all needed depdencies (solr, db, redis)

* Install latest version of docker and docker-compose
* `bin/start.sh`
* `bin/initialize_db.sh`

## Installing the odata.org.il ckan extensions and settings on an existing ckan project

### install the odata.org.il extension

This extension overrides templates and other code to provide the odata.org.il theme and logic changes.

* Install the package (should run inside your ckan installations virtualenv):
  * `pip install -e 'git+https://github.com/OriHoch/data4dappl.git#egg=ckanext-odata_org_il&subdirectory=ckan/ckanext-odata_org_il'`
* Edit the configuration (E.g. /etc/ckan/default/development.ini)
  * add odata_org_il to ckan.plugins
* restart ckan

### install the google analytics extension

Optional - provides good integration of ckan with google analytics.

See [ckanext-googleanalytics](https://github.com/ckan/ckanext-googleanalytics) for more details.

* Install the extension and dependencies (inside the Python virtualenv)
  * `ckan/install_analytics.sh`
* Add the following to your development.ini:
  * googleanalytics.id = UA-1010101-1
  * googleanalytics.account = Account name (i.e. data.gov.uk, see top level item at https://www.google.com/analytics)
* add `googleanalytics` to `ckan.plugins` in your development.ini
