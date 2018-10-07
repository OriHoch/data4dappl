from datapackage_pipelines.utilities.resources import PROP_STREAMING
from datapackage_pipelines.wrapper import ingest, spew
from collections import defaultdict
import logging, requests
from itertools import chain
from os import environ


CKAN_API_KEY = environ.get('CKAN_API_KEY')
CKAN_URL = environ.get('CKAN_URL')
assert CKAN_API_KEY and CKAN_URL
CKAN_AUTH_HEADERS = {'Authorization': CKAN_API_KEY}


def get_groups_page(limit, offset):
    groups_res = requests.post('{}/api/3/action/group_list'.format(CKAN_URL),
                               data={'all_fields': True, 'include_dataset_count': False, 'include_extras': True,
                                     'limit': limit, 'offset': offset},
                               headers=CKAN_AUTH_HEADERS).json()
    assert groups_res and groups_res['success']
    return groups_res['result']


def get_existing_entities_resource(stats):
    limit = 500
    logging.info('Loading existing entities / groups, {} results per page'.format(limit))
    offset = 0
    while True:
        logging.info('offset={}'.format(offset))
        groups = get_groups_page(limit, offset)
        if len(groups) == 0:
            break
        for group in groups:
            entity_ids = [extra['value'] for extra in group['extras'] if extra['key'] == 'entity_id']
            if len(entity_ids) == 0:
                entity_id = ''
                stats['existing_groups_without_entity'] += 1
            elif len(entity_ids) == 1:
                entity_id = entity_ids[0]
                stats['existing_groups_with_entity'] += 1
            else:
                raise Exception('multiple entity id extra fields found')
            yield {'title': group['title'],
                   'group_id': group['id'],
                   'group_name': group['name'],
                   'entity_id': entity_id,
                   'group': group}
        # logging.info(stats)
        offset += limit


def get_existing_entities_resource_descriptor():
    return {'name': 'existing_entities',
            'path': 'existing_entities.csv',
            PROP_STREAMING: True,
            'schema': {'fields': [{'name': name, 'type': 'string'}
                                  for name in ['title', 'group_id', 'group_name', 'entity_id']] +
                                 [{'name': 'group', 'type': 'object'}]}}


def main():
    parameters, datapackage, resources, stats = ingest() + (defaultdict(int),)
    datapackage['resources'].append(get_existing_entities_resource_descriptor())
    spew(datapackage, chain(resources, [get_existing_entities_resource(stats)]), stats)


if __name__ == '__main__':
    main()

