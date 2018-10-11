from datapackage_pipelines.utilities.resources import PROP_STREAMING
from datapackage_pipelines.wrapper import ingest, spew
from collections import defaultdict
import requests
import logging
from os import environ


CKAN_API_KEY = environ.get('CKAN_API_KEY')
CKAN_URL = environ.get('CKAN_URL')
assert CKAN_API_KEY and CKAN_URL
CKAN_AUTH_HEADERS = {'Authorization': CKAN_API_KEY}


def get_existing_entities(resource, existing_entities, stats):
    [existing_entities.setdefault(v, {}) for v in ['titles', 'entity_ids', 'groups']]
    for row in resource:
        entity_id = row['entity_id']
        title = row['title']
        group_id = row['group_id']
        group_name = row['group_name']
        existing_entities['groups'][group_id] = row['group']
        existing_entities['groups'][group_name] = row['group']
        if entity_id:
            existing_entities['entity_ids'][entity_id] = group_id
        elif title in existing_entities['titles']:
            existing_entities['titles'][title] = None
        else:
            existing_entities['titles'][title] = group_id
        yield row


def get_foi_groups_matching(resource, existing_entities, stats):
    existing_entities.setdefault('entity_ids', {})
    for row in resource:
        entity_id = row['entity_id']
        group_id = row['Column3']
        if entity_id and group_id:
            stats['foi_groups_matching_entity'] += 1
            existing_entities['entity_ids'][entity_id] = group_id
        else:
            stats['foi_groups_not_matching_entity'] += 1
        yield row


def get_foi_offices_resource(resource, existing_entities, stats, dry_run):
    session = requests.session()
    session.headers.update(CKAN_AUTH_HEADERS)
    for row in resource:
        title = '{}: {}'.format(row['mmdOfficesTypes'], row['title'])
        state = 'active'
        entity_id = 'foi-office-{}'.format(row['nid'])
        extras = [{'key': k, 'value': str(v)}
                  for k, v in row.items()
                  if k != 'title']
        extras.append({'key': 'entity_id', 'value': entity_id})
        group_id = existing_entities['entity_ids'].get(entity_id)
        if group_id:
            stats['update_existing_entity_by_entity_id'] += 1
        else:
            group_id = existing_entities['titles'].get(row['title'])
            if group_id:
                stats['update_existing_entity_by_title'] += 1
        if group_id:
            extras_dict = {e['key']: e['value'] for e in extras}
            existing_group = existing_entities['groups'].get(group_id)
            existing_group_extras_dict = {e['key']: e['value'] for e in existing_group.pop('extras', [])}
            if len([True for k, v in extras_dict.items() if existing_group_extras_dict.get(k) != v]) > 0:
                logging.info('updating group id {}'.format(group_id))
                update_type = 'update'
                stats['updated_entities'] += 1
                extras = [{'key': k, 'value': v} for k, v in extras_dict.items()]
                if not dry_run:
                    group_update_res = session.post('{}/api/3/action/group_patch'.format(CKAN_URL),
                                                    json=dict(id=group_id, extras=extras)).json()
            else:
                # logging.info('no update needed for group_id {}'.format(group_id))
                update_type = 'none'
                stats['no_update_needed_entities'] += 1
                group_update_res = None
        else:
            logging.info('creating group with entity id {}'.format(entity_id))
            update_type = 'create'
            stats['created_entities'] += 1
            if not dry_run:
                group_update_res = session.post('{}/api/3/action/group_create'.format(CKAN_URL),
                                                json=dict(name=entity_id, title=title,
                                                          state=state, extras=extras)).json()
        if not dry_run:
            assert update_type == 'none' or (group_update_res and group_update_res.get('success')), str(group_update_res)
        yield dict(row, update_type=update_type, update_title=title, entity_id=entity_id)


def main():
    parameters, datapackage, resources, stats = ingest() + (defaultdict(int),)
    resource_names = [r['name'] for r in datapackage['resources']]
    datapackage['resources'] = [r for r in datapackage['resources'] if r['name'] == 'foi_offices']
    datapackage['resources'][0]['schema']['fields'] += [{'name': 'update_type', 'type': 'string'},
                                                        {'name': 'update_title', 'type': 'string'},
                                                        {'name': 'entity_id', 'type': 'string'},]

    def get_resources():
        existing_entities = {}
        for resource_name, resource in zip(resource_names, resources):
            if resource_name == 'existing_entities':
                for row in get_existing_entities(resource, existing_entities, stats):
                    pass
            elif resource_name == 'foi-groups-matching':
                for row in get_foi_groups_matching(resource, existing_entities, stats):
                    pass
            elif resource_name == 'foi_offices':
                yield get_foi_offices_resource(resource, existing_entities, stats, parameters.get('dry-run'))
            else:
                for row in resource:
                    pass

    spew(datapackage, get_resources(), stats)


if __name__ == '__main__':
    main()

