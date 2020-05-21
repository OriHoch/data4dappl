# data4dappl

A web-site with additional pipelines and data processing that allow to browse and analyze data received from freedom of information requests sent by a group of Israeli lawyers and organizations.

The site is available here: https://www.odata.org.il/en/

## Development Quickstart

#### Using local CKAN backed by Docker based infrastructure

* Verify Python version, it should be Python 2.7: `python --version`
* Install Python virtualenv: `sudo apt-get install python-virtualenv`
* Install Docker & Docker Compose

###### Install (should be done once)

```
mkdir venv
virtualenv --no-site-packages venv
. venv/bin/activate
pip install setuptools==36.1
pip install -e 'git+https://github.com/hasadna/ckan.git@master#egg=ckan'
pip install -r venv/src/ckan/requirements.txt
docker-compose up -d
docker-compose exec -u postgres db createuser -S -D -R -P ckan_default
docker-compose exec -u postgres db createdb -O ckan_default ckan_default -E utf-8
mkdir venv/etc
paster make-config ckan venv/etc/development.ini
ln -s `pwd`/venv/src/ckan/who.ini `pwd`/venv/etc/who.ini
mkdir venv/storage
```

Edit the created config file (`venv/etc/development.ini`) and set the following:

```
sqlalchemy.url = postgresql://ckan_default:pass@127.0.0.1/ckan_default
solr_url = http://127.0.0.1:8983/solr/ckan
ckan.site_url = http://localhost:5000
ckan.storage_path = /absolute/path/to/venv/storage
```

Create the DB tables:

```
cd venv/src/ckan
paster db init -c `pwd`/../../etc/development.ini
```

Install the odata plugin:

```
pip install -r ckan/requirements-odata.txt
pip install -e ckan/ckanext-odata_org_il
```

Edit the configuration (`venv/etc/development.ini`) and add `odata_org_il` to ckan.plugins

###### Start dev server

```
docker-compose up -d
. venv/bin/activate
( cd venv/src/ckan && paster serve `pwd`/../../etc/development.ini )
```

Create admin user

```
( cd venv/src/ckan && paster sysadmin add admin -c `pwd`/../../etc/development.ini )
```

#### Using local CKAN instlalation

See the [Installing CKAN 2.8 Documentation](https://docs.ckan.org/en/2.8/maintaining/installing/index.html) to get a local CKAN installed for development. 

For development it's recommended to install CKAN from source.

Install the odata plugin:

* Install dependencies:
  * `pip install -r /path/to/data4dappl/ckan/requirements-odata.txt`
* Install the package:
  * `pip install -e /path/to/data4dappl/ckan/ckanext-odata_org_il`
* Edit the configuration (E.g. /etc/ckan/default/development.ini)
  * add odata_org_il to ckan.plugins
* restart ckan

#### Using Minikube

This method is more complex but allows to get an environment which is almost identical to the production environment.

Fork and clone [hasadna/hasadna-k8s](https://github.com/hasadna/hasadna-k8s) and follow the [odata chart docs](https://github.com/hasadna/hasadna-k8s/blob/master/charts-external/odata/README.md) to setup a minikube environment.

The following script builds local docker image, send to minikube and starts port forwarding

```
docker build -t odata-ckan ckan &&\
bin/minikube_patch_image.sh ckan odata-ckan &&\
bin/minikube_port_forward.sh ckan 5000
```

Ckan should be available at http://localhost:5000

To speedup update of the ckan pod, you can set lower termination grace period

```
bin/minikube_kubectl.sh get deployment ckan -o yaml \
    | sed 's/terminationGracePeriodSeconds: 30/terminationGracePeriodSeconds: 1/g' \
    | bin/minikube_kubectl.sh replace -f -
```

For even faster development flow, you can run ckan locally but connect to the minikube infrastructure

The following command creates a ckan configuration file at ckan/development-local.ini (if it doesn't exist)

It then starts port forwards for all the infrastructure ports to localhost

```
bin/minikube_local_development.sh
```

You can delete the ckan deployment: `kubectl delete deployment ckan`

We use [pipenv](https://docs.pipenv.org/) to manage the virtualenv and handle the dependencies

Install the required dependencies

```
bin/install.sh
```

Start ckan

```
pipenv run gunicorn --paste ckan/development-local.ini
```

Ckan is available at http://localhost:5000

Rebuild the search index

```
pipenv run paster --plugin=ckan search-index -c ckan/development-local.ini rebuild
```

## Translations

Translations are done in Transifex:

* Translations of core CKAN strings: https://www.transifex.com/the-public-knowledge-workshop/hasadna-ckan
* Translations of odata specific strings: https://www.transifex.com/the-public-knowledge-workshop/odata-org-il

### Updating translations code

Changes to core ckan are managed in [hasadna/ckan](https://github.com/hasadna/ckan).

Unique strings which are relevant only for odata are managed locally in the odata-org-il extension.

Update the .pot file - should be done in case of additional / modified strings in the templates

```
( cd ckan/ckanext-odata_org_il && python setup.py extract_messages )
```

Edit the .pot file and remove core ckan strings (which are there only because of extending core ckan templates)

Leave only strings unique to odata

Push the pot file to transifex

```
( cd ckan/ckanext-odata_org_il && tx push --source )
```

Translate and update the translations in transifex

Pull updated transifex translations

```
( cd ckan/ckanext-odata_org_il && tx pull -fl he,ar )
```

Compile mo files:

```
msgfmt -o ckan/ckanext-odata_org_il/ckanext/odata_org_il/i18n/ar/LC_MESSAGES/ckanext-odata_org_il.mo \
          ckan/ckanext-odata_org_il/ckanext/odata_org_il/i18n/ar/LC_MESSAGES/ckanext-odata_org_il.po &&\
msgfmt -o ckan/ckanext-odata_org_il/ckanext/odata_org_il/i18n/he/LC_MESSAGES/ckanext-odata_org_il.mo \
          ckan/ckanext-odata_org_il/ckanext/odata_org_il/i18n/he/LC_MESSAGES/ckanext-odata_org_il.po
```

Commit
