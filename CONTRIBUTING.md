# Contributing to מידע לעם

* Welcome to מידע לעם
* Contributions of any kind are welcome.

## odata pipelines development workflow

Set environment variables (you can get the API key from an admin CKAN user's profile page):

```
export CKAN_URL=https://www.odata.org.il/
export CKAN_API_KEY=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX 
```

Start a bash terminal on a pipelines server docker container with mounting of relevant volumes

```
docker run \
  -v `pwd`/ckan/ckanext-odata_org_il/ckanext/odata_org_il/pipelines:/pipelines/ckanext-odata_org_il \
  -v `pwd`/ckan/ckanext-odata_org_il/ckanext/odata_org_il/pipelines/data:/var/lib/ckan/data/pipelines/odata_org_il \
  -e CKAN_URL=$CKAN_URL -e CKAN_API_KEY=$CKAN_API_KEY \
  -it --entrypoint bash orihoch/datapackage-pipelines-ckanext:v0.0.4
```

Get the list of available pipelines:

```
dpp
```

Run a pipeline:

```
dpp run ./ckanext-odata_org_il/download_foi_offices_xml
```

Inside the Docker container, pipeline data should be available under `/var/lib/ckan/data/pipelines/odata_org_il/`

Outside of the Docker container, pipeline data should be available under the project root at `ckan/ckanext-odata_org_il/ckanext/odata_org_il/pipelines/data/`

To access the data outside of the Docker container, you might need to change ownership

From inside the container (change the UID if needed): `chown -R 1000 /var/lib/ckan/data/pipelines/odata_org_il/`

From outside the container: `sudo chown -R $USER ckan/ckanext-odata_org_il/ckanext/odata_org_il/pipelines/data/`
