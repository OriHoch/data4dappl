# data4dappl

A web-site with additional pipelines and data processing that allow to browse and analyze data received from freedom of information requests sent by a group of Israeli lawyers and organizations.

The site is available here: https://www.odata.org.il/en/

## Development Quickstart

We use minikube to get a running environment which you can then do local development on

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

## Installing the ckan extension on an existing ckan project

If you have an existing ckan installation and just want to install the odata plugin:

* Install the package (should run inside your ckan installations virtualenv):
  * `pip install -e 'git+https://github.com/OriHoch/data4dappl.git#egg=ckanext-odata_org_il&subdirectory=ckan/ckanext-odata_org_il'`
* Edit the configuration (E.g. /etc/ckan/default/development.ini)
  * add odata_org_il to ckan.plugins
* restart ckan

## Translations

Translations are done in Transifex:

* Translations of core CKAN strings: https://www.transifex.com/the-public-knowledge-workshop/hasadna-ckan
* Translations of odata specific strings: https://www.transifex.com/the-public-knowledge-workshop/odata-org-il

### Updating translations code

Changes to core ckan are managed in [hasadna/ckan](https://github.com/hasadna/ckan).

Unique strings which are relevant only for odata are managed locally in the odata-org-il extension.

Update the .pot file - should be done in case of additional / modified strings in the templates

```
( cd ckan/ckanext-odata_org_il/ckanext && python setup.py extract_messages )
```

Edit the .pot file and remove core ckan strings (which are there only because of extending core ckan templates)

Leave only strings unique to odata

Push the pot file to transifex

```
( cd ckan/ckanext-odata_org_il/ckanext && tx push --source )
```

Translate and update the translations in transifex

Pull updated transifex translations

```
( cd ckan/ckanext-odata_org_il/ckanext && tx pull -fl he,ar )
```

Compile mo files:

```
msgfmt -o ckan/ckanext-odata_org_il/ckanext/odata_org_il/i18n/ar/LC_MESSAGES/ckanext-odata_org_il.mo \
          ckan/ckanext-odata_org_il/ckanext/odata_org_il/i18n/ar/LC_MESSAGES/ckanext-odata_org_il.po &&\
msgfmt -o ckan/ckanext-odata_org_il/ckanext/odata_org_il/i18n/he/LC_MESSAGES/ckanext-odata_org_il.mo \
          ckan/ckanext-odata_org_il/ckanext/odata_org_il/i18n/he/LC_MESSAGES/ckanext-odata_org_il.po
```

Commit
