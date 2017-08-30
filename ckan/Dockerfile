FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y python-dev libpq-dev python-pip python-virtualenv git-core

COPY requirement-setuptools.txt /requirement-setuptools.txt
COPY requirements-ckan.txt /requirements-ckan.txt
RUN pip install -r /requirement-setuptools.txt
RUN pip install -r /requirements-ckan.txt
RUN pip install -e 'git+https://github.com/ckan/ckan.git@ckan-2.7.0#egg=ckan'

# install the ckan google analytics extension
COPY ckanext-googleanalytics-requirements.txt /ckanext-googleanalytics-requirements.txt
RUN pip install 'git+https://github.com/ckan/ckanext-googleanalytics.git@7c805cd7b2ee18ec6dfceadf1e04e3f024620db4#egg=ckanext-googleanalytics'
RUN pip install -r /ckanext-googleanalytics-requirements.txt

COPY development.ini development.ini
COPY who.ini who.ini

COPY ckanext-odata_org_il /ckanext-odata_org_il
RUN pip install -e /ckanext-odata_org_il

CMD ["serve", "development.ini"]

ENTRYPOINT ["paster"]
