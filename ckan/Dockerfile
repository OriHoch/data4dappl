FROM orihoch/ckan-2.8.1-fix-autocomplete-keycodes

USER root

COPY development.ini /etc/ckan/default/development.ini
COPY who.ini /etc/ckan/default/who.ini

COPY ckanext-odata_org_il /ckanext-odata_org_il
RUN ckan-pip install -e /ckanext-odata_org_il

RUN find /ckanext-odata_org_il -name '*.pyc' -delete &&\
    find /usr/lib/ckan -name '*.pyc' -delete

RUN chown -R ckan:ckan /etc/ckan /usr/lib/ckan /var/lib/ckan

COPY entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

USER ckan

WORKDIR "/usr/lib/ckan/venv"

CMD ["server", "start"]
