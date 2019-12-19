FROM uumpa/hasadna-ckan:v2.8.2.1

USER root

COPY ckanext-odata_org_il/ $CKAN_VENV/src/ckanext-odata_org_il/
RUN chown -R ckan:ckan $CKAN_VENV/src/ckanext-odata_org_il

USER ckan

RUN ckan-pip install -e $CKAN_VENV/src/ckanext-odata_org_il/

COPY requirements-odata.txt /
RUN ckan-pip install -r /requirements-odata.txt && ckan-pip install -U requests[security]
