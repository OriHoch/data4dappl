from datapackage_pipelines.utilities.resources import PROP_STREAMING
from datapackage_pipelines.wrapper import ingest, spew
from collections import defaultdict
import requests
import logging
from os import environ
import hashlib


CKAN_API_KEY = environ.get('CKAN_API_KEY')
CKAN_URL = environ.get('CKAN_URL')
assert CKAN_API_KEY and CKAN_URL
CKAN_AUTH_HEADERS = {'Authorization': CKAN_API_KEY}


def string_munge(str):
    str = str.replace('-', ' ')
    while True:
        new_str = str.replace('  ', ' ')
        if len(new_str) == len(str):
            break
        str = new_str
    return str.strip()


def get_existing_entities(resource, existing_entities, stats):
    [existing_entities.setdefault(v, {}) for v in ['munged_titles', 'entity_ids', 'groups']]
    for row in resource:
        group_id = row['group_id'].strip()
        assert group_id and group_id not in existing_entities['groups']
        group_name = row['group_name'].strip()
        assert group_name and group_name not in existing_entities['groups']
        # both group id and name are used to uniquely reference groups in CKAN
        # we only care about the group extras which contains the auto-updated data
        group_extras = {e['key'].lower(): e['value'].strip() for e in row['group']['extras']}
        group = {'id': group_id, 'name': group_name, 'extras': group_extras}
        existing_entities['groups'][group_id] = group
        existing_entities['groups'][group_name] = group
        entity_id = group_extras.get('entity_id')
        if entity_id:
            stats['existing_groups_with_entity_id'] += 1
            existing_entities['entity_ids'][entity_id] = group_id
        else:
            munged_group_title = string_munge(row.get('title').strip())
            assert munged_group_title not in existing_entities['munged_titles']
            existing_entities['munged_titles'][munged_group_title] = group_id
            stats['existing_groups_with_munged_title'] += 1
        yield row


def get_foi_groups_matching(resource, existing_entities, stats):
    existing_entities.setdefault('entity_ids', {})
    for row in resource:
        entity_id = row['entity_id']
        group_id = row['Column3']
        if entity_id and group_id:
            if entity_id not in existing_entities['entity_ids']:
                stats['foi_groups_matching_has_group_entity'] += 1
                existing_entities['entity_ids'][entity_id] = group_id
            else:
                group = existing_entities['groups'][group_id]
                existing_entity_group_id = existing_entities['entity_ids'][entity_id]
                if group['id'] != existing_entity_group_id and group['name'] != existing_entity_group_id:
                    raise Exception('duplicate entity_ids for different groups: {} {}'.format(entity_id, group_id))
                stats['foi_groups_matching_same_entity_group_entity'] += 1
        else:
            stats['foi_groups_matching_no_group_entity'] += 1
        yield row


def get_foi_offices_xml(resource, existing_entities, stats):
    entities = {}
    for row in resource:
        row = {k.lower(): (v.strip() if v else '') for k, v in row.items()}
        title_hash = hashlib.md5(row['title'].encode()).hexdigest()
        entity_id = 'foi-{}-{}-{}'.format(row['officetypecode'], row['officenamecode'], title_hash)
        assert entity_id not in entities
        entities[entity_id] = dict(row, **{'__type': 'xml'})
        stats['foi_office_xml_entities'] += 1
        yield row
    existing_entities['xml_entities'] = entities


def get_foi_offices_json(resource, existing_entities, stats):
    entities = {}
    for row in resource:
        row = {k.lower(): (v.strip() if v else '') for k, v in row.items()}
        entity_id = 'foi-office-{}'.format(row['nid'])
        assert entity_id not in entities
        entities[entity_id] = dict(row, **{'__type': 'json'})
        stats['foi_office_json_entities'] += 1
        yield row
    existing_entities['json_entities'] = entities


def merge_json_xml_rows(json_row, xml_row):
    lower_xml_keys = [k.lower() for k in xml_row]
    for k, v in json_row.items():
        if k.lower() not in lower_xml_keys:
            xml_row[k] = v
    return xml_row


def update_foi_offices_entities(existing_entities, stats, dry_run):
    session = requests.session()
    session.headers.update(CKAN_AUTH_HEADERS)
    xml_entities = existing_entities['xml_entities']
    json_entities = existing_entities['json_entities']
    munged_titles = []
    for entities in (xml_entities, json_entities):
        for entity_id, row in entities.items():
            row['entity_id'] = entity_id
            row_title = row['title'].strip()
            assert row_title, 'missing title: {}'.format(row)
            mmd_offices_types = row['mmdofficestypes'].strip()
            assert mmd_offices_types, 'missing mmd_offices_types: {}'.format(row)
            munged_title = string_munge('{} {}'.format(mmd_offices_types, row_title))
            assert munged_title not in munged_titles, 'duplicate title: {}'.format(row)
            extras = [{'key': k.lower(), 'value': str(v).strip()}
                      for k, v in row.items()
                      if k not in ['title', 'Title']]
            entity_group_id = existing_entities['entity_ids'].get(entity_id)
            if entity_group_id:
                stats['update_existing_group_by_entity_id'] += 1
            else:
                entity_group_id = existing_entities['munged_titles'].get(munged_title)
                if entity_group_id:
                    stats['update_existing_group_by_munged_title'] += 1
            if entity_group_id:
                old_extras = {e['key'].lower(): e['value'].strip() for e in existing_entities['groups'][entity_group_id]['extras']}
                logging.info(old_extras)
                new_extras = {e['key'].lower(): e['value'].strip() for e in extras}
                logging.info(new_extras)
                has_differences = len([True for k, v in new_extras.items() if old_extras.get(k) != v]) > 0
                if has_differences:
                    logging.info('patching group id {}'.format(entity_group_id))
                    update_type = 'patch'
                    stats['patched_entities'] += 1
                    extras = [{'key': k, 'value': v} for k, v in dict(old_extras, **new_extras).items()]
                    if not dry_run:
                        res = session.post('{}/api/3/action/group_package_show'.format(CKAN_URL),
                                           data={'id': entity_group_id, 'include_extras': True, 'limit': 500}, ).json()
                        assert res and res['success'], str(res)
                        group_dataset_ids = [package['id'] for package in res['result']]
                        assert len(group_dataset_ids) < 499, 'too many datasets for group id {}'.format(entity_group_id)
                        logging.info('patching group, will restore {} datasets'.format(len(group_dataset_ids)))
                        group_update_res = session.post('{}/api/3/action/group_patch'.format(CKAN_URL),
                                                        json=dict(id=entity_group_id, extras=extras)).json()
                        assert group_update_res and group_update_res.get('success'), str(group_update_res)
                        for dataset_id in group_dataset_ids:
                            logging.info('restoring dataset {} to group {}'.format(dataset_id, entity_group_id))
                            res = session.post('{}/api/3/action/member_create'.format(CKAN_URL),
                                               json=dict(id=entity_group_id, object=dataset_id, object_type='package',
                                                         capacity='')).json()
                            assert res and res['success'], str(res)





            # this title is used for new entities only
            # updated entities titles are not changed
            new_entity_title = '{}: {}'.format(mmd_offices_types, row_title)

            extras = [{'key': k, 'value': str(v)}
                      for k, v in row.items()
                      if k not in ['title', 'Title']]
            if group_id:
                stats['update_existing_entity_by_entity_id'] += 1
            else:
                group_id = existing_entities['titles'].get(title)
                if group_id:
                    stats['update_existing_entity_by_title'] += 1
            if group_id:
                extras_dict = {e['key']: e['value'] for e in extras}
                existing_group = existing_entities['groups'].get(group_id)
                existing_group_extras_dict = {e['key']: e['value'] for e in existing_group.pop('extras', [])}
                if len([True for k, v in extras_dict.items() if existing_group_extras_dict.get(k) != v]) > 0:
                    logging.info('patching group id {}'.format(group_id))
                    update_type = 'patch'
                    stats['patched_entities'] += 1
                    extras = [{'key': k, 'value': v} for k, v in extras_dict.items()]
                    if not dry_run:
                        res = session.post('{}/api/3/action/group_package_show'.format(CKAN_URL),
                                           data={'id': group_id, 'include_extras': True, 'limit': 500}, ).json()
                        assert res and res['success'], str(res)
                        group_dataset_ids = [package['id'] for package in res['result']]
                        assert len(group_dataset_ids) < 499, 'too many datasets for group id {}'.format(group_id)
                        logging.info('patching group, will restore {} datasets'.format(len(group_dataset_ids)))
                        group_update_res = session.post('{}/api/3/action/group_patch'.format(CKAN_URL),
                                                        json=dict(id=group_id, extras=extras)).json()
                        assert group_update_res and group_update_res.get('success'), str(group_update_res)
                        for dataset_id in group_dataset_ids:
                            logging.info('restoring dataset {} to group {}'.format(dataset_id, group_id))
                            res = session.post('{}/api/3/action/member_create'.format(CKAN_URL),
                                               json=dict(id=group_id, object=dataset_id, object_type='package',
                                                         capacity='')).json()
                            assert res and res['success'], str(res)
                else:
                    # logging.info('no update needed for group_id {}'.format(group_id))
                    update_type = 'none'
                    stats['no_update_needed_entities'] += 1
            else:
                logging.info('creating group with entity id {}'.format(entity_id))
                update_type = 'create'
                stats['created_entities'] += 1
                if not dry_run:
                    group_update_res = session.post('{}/api/3/action/group_create'.format(CKAN_URL),
                                                    json=dict(name=entity_id, title=title,
                                                              state='active', extras=extras)).json()
                    assert group_update_res and group_update_res.get('success'), str(group_update_res)
            yield dict(row, update_type=update_type, update_title=title, entity_id=entity_id)

    exit(1)

    logging.info(stats)
    exit(1)
    titles_rows = {}
    for entity_id, row in entity_id_rows:
        row['entity_id'] = entity_id
        row_title = row.get('Title', row.get('title'))
        assert row_title, 'missing title: {}'.format(row)
        mmd_offices_types = row['mmdOfficesTypes' if row['__type'] == 'json' else 'MMDOfficesTypes']
        assert mmd_offices_types, 'missing mmd_offices_types: {}'.format(row)
        row_title = string_munge(row_title)
        mmd_offices_types = string_munge(mmd_offices_types)
        title = '{}: {}'.format(mmd_offices_types, row_title)
        if title in titles_rows:
            logging.info('merging json and xml rows on title: {} {}'.format(entity_id, titles_rows[title]['entity_id']))
            stats['duplicate_title_using_json'] += 1
            if row['__type'] == 'json':
                titles_rows[title] = merge_json_xml_rows(row, titles_rows[title])
            else:
                titles_rows[title] = merge_json_xml_rows(titles_rows[title], row)
        else:
            titles_rows[title] = row
    stats['unique_entity_titles'] = len(titles_rows)
    session = requests.session()
    session.headers.update(CKAN_AUTH_HEADERS)
    for title, row in titles_rows.items():
        entity_id = row['entity_id']
        group_id = existing_entities['entity_ids'].get(entity_id)
        extras = [{'key': k, 'value': str(v)}
                  for k, v in row.items()
                  if k not in ['title', 'Title']]
        if group_id:
            stats['update_existing_entity_by_entity_id'] += 1
        else:
            group_id = existing_entities['titles'].get(title)
            if group_id:
                stats['update_existing_entity_by_title'] += 1
        if group_id:
            extras_dict = {e['key']: e['value'] for e in extras}
            existing_group = existing_entities['groups'].get(group_id)
            existing_group_extras_dict = {e['key']: e['value'] for e in existing_group.pop('extras', [])}
            if len([True for k, v in extras_dict.items() if existing_group_extras_dict.get(k) != v]) > 0:
                logging.info('patching group id {}'.format(group_id))
                update_type = 'patch'
                stats['patched_entities'] += 1
                extras = [{'key': k, 'value': v} for k, v in extras_dict.items()]
                if not dry_run:
                    res = session.post('{}/api/3/action/group_package_show'.format(CKAN_URL),
                                       data={'id': group_id, 'include_extras': True, 'limit': 500}, ).json()
                    assert res and res['success'], str(res)
                    group_dataset_ids = [package['id'] for package in res['result']]
                    assert len(group_dataset_ids) < 499, 'too many datasets for group id {}'.format(group_id)
                    logging.info('patching group, will restore {} datasets'.format(len(group_dataset_ids)))
                    group_update_res = session.post('{}/api/3/action/group_patch'.format(CKAN_URL),
                                                    json=dict(id=group_id, extras=extras)).json()
                    assert group_update_res and group_update_res.get('success'), str(group_update_res)
                    for dataset_id in group_dataset_ids:
                        logging.info('restoring dataset {} to group {}'.format(dataset_id, group_id))
                        res = session.post('{}/api/3/action/member_create'.format(CKAN_URL),
                                           json=dict(id=group_id, object=dataset_id, object_type='package', capacity='')).json()
                        assert res and res['success'], str(res)
            else:
                # logging.info('no update needed for group_id {}'.format(group_id))
                update_type = 'none'
                stats['no_update_needed_entities'] += 1
        else:
            logging.info('creating group with entity id {}'.format(entity_id))
            update_type = 'create'
            stats['created_entities'] += 1
            if not dry_run:
                group_update_res = session.post('{}/api/3/action/group_create'.format(CKAN_URL),
                                                json=dict(name=entity_id, title=title,
                                                          state='active', extras=extras)).json()
                assert group_update_res and group_update_res.get('success'), str(group_update_res)
        yield dict(row, update_type=update_type, update_title=title, entity_id=entity_id)


def main():
    parameters, datapackage, resources, stats = ingest() + (defaultdict(int),)
    resource_names = [r['name'] for r in datapackage['resources']]
    json_descriptor = [r for r in datapackage['resources'] if r['name'] == 'foi_offices'][0]
    xml_descriptor = [r for r in datapackage['resources'] if r['name'] == 'foi_offices_xml'][0]
    combined_descriptor = dict(json_descriptor, schema={'fields': []})
    field_names = []
    for field in xml_descriptor['schema']['fields']:
        field['name'] = field['name'].lower()
        if field['name'] not in field_names:
            field_names.append(field['name'])
            combined_descriptor['schema']['fields'] += [field]
    for field in json_descriptor['schema']['fields']:
        field['name'] = field['name'].lower()
        if field['name'] not in field_names:
            field_names.append(field['name'])
            combined_descriptor['schema']['fields'] += [field]
    combined_descriptor['schema']['fields'] += [{'name': 'update_type', 'type': 'string'},
                                                {'name': 'update_title', 'type': 'string'},
                                                {'name': 'entity_id', 'type': 'string'},
                                                {'name': '__type', 'type': 'string'},]
    datapackage['resources'] = [combined_descriptor]

    def get_resources():
        existing_entities = {}
        for resource_name, resource in zip(resource_names, resources):
            if resource_name == 'existing_entities':
                for row in get_existing_entities(resource, existing_entities, stats):
                    pass
            elif resource_name == 'foi-groups-matching':
                for row in get_foi_groups_matching(resource, existing_entities, stats):
                    pass
            elif resource_name == 'foi_offices_xml':
                for row in get_foi_offices_xml(resource, existing_entities, stats):
                    pass
            elif resource_name == 'foi_offices':
                for row in get_foi_offices_json(resource, existing_entities, stats):
                    pass
                yield update_foi_offices_entities(existing_entities, stats, parameters.get('dry-run'))
            else:
                for row in resource:
                    pass

    spew(datapackage, get_resources(), stats)


if __name__ == '__main__':
    main()

