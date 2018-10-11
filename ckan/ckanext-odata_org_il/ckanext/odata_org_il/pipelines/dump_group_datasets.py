from datapackage_pipelines.utilities.resources import PROP_STREAMING
from datapackage_pipelines.wrapper import ingest, spew
from collections import defaultdict
import logging, requests
from itertools import zip_longest
from os import environ


CKAN_API_KEY = environ.get('CKAN_API_KEY')
CKAN_URL = environ.get('CKAN_URL')
assert CKAN_API_KEY and CKAN_URL
CKAN_AUTH_HEADERS = {'Authorization': CKAN_API_KEY}


def get_group_datasets(group_id):
    res = requests.post('{}/api/3/action/group_package_show'.format(CKAN_URL),
                               data={'id': group_id, 'include_extras': True,
                                     'limit': 500},
                               headers=CKAN_AUTH_HEADERS).json()
    assert res and res['success']
    return res['result']


def get_group_dataset_ids(group_id):
    for dataset in get_group_datasets(group_id):
        yield dataset['id']


def get_resources(resources, descriptors):
    group_ids = set()

    def get_existing_entities_resource(resource):
        for row in resource:
            group_ids.add(row['group_id'])
            yield row

    def get_group_datasets_resource():
        for group_id in group_ids:
            dataset_ids = list(get_group_dataset_ids(group_id))
            yield {'group_id': group_id, 'dataset_ids': dataset_ids}

    for resource, descriptor in zip_longest(resources, descriptors):
        if descriptor['name'] == 'existing_entities':
            yield get_existing_entities_resource(resource)
        elif descriptor['name'] == 'group_datasets':
            yield get_group_datasets_resource()


def get_group_datasets_resource_descriptor():
    return {'name': 'group_datasets',
            'path': 'group_datasets.csv',
            PROP_STREAMING: True,
            'schema': {'fields': [{'name': 'group_id', 'type': 'string'},
                                  {'name': 'dataset_ids', 'type': 'array'}]}}


def main():
    parameters, datapackage, resources, stats = ingest() + (defaultdict(int),)
    datapackage['resources'].append(get_group_datasets_resource_descriptor())
    spew(datapackage, get_resources(resources, datapackage['resources']), stats)


if __name__ == '__main__':
    main()

