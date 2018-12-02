import sys
from datapackage_pipelines.utilities.resources import PROP_STREAMING
from datapackage_pipelines.wrapper import ingest, spew
import os
import requests
import datetime
import json
from time import sleep
import logging
from itertools import chain


SCHEMAS = {
    'groups': {'fields': [{'name': n, 'type': t} for n, t in {
        'users': 'array',
        'display_name': 'string',
        'description': 'string',
        'image_display_url': 'string',
        'type': 'boolean',
        'created': 'datetime',
        'name': 'string',
        'is_organization': 'boolean',
        'state': 'string',
        'extras': 'array',
        'image_url': 'string',
        'title': 'string',
        'revision_id': 'string',
        'num_followers': 'integer',
        'id': 'string'
    }.items()]},
    'users': {'fields': [{'name': n, 'type': t} for n, t in {
        'display_name': 'string',
        'name': 'string',
        'created': 'datetime',
        'id': 'string',
        'sysadmin': 'boolean',
        'state': 'string',
        'fullname': 'string',
        'email': 'string',
        'number_created_packages': 'integer',
        'number_of_edits': 'integer'
    }.items()]}
}

SCHEMAS['organizations'] = json.loads(json.dumps(SCHEMAS['groups']))

ROWS_PER_PAGE = {
    'groups': 100,
    'organizations': 100
}

INITIAL_REQUEST_DATA = {
    'groups': {'all_fields': True, 'include_dataset_count': False, 'include_extras': True, 'include_users': True},
    'organizations': {'all_fields': True, 'include_dataset_count': False, 'include_extras': True, 'include_users': True},
    'users': {'all_fields': True}
}

ACTION_URL_PATH = {
    'groups': '/api/3/action/group_list',
    'organizations': '/api/3/action/organization_list',
    'users': '/api/3/action/user_list',
    'member_create': '/api/3/action/member_create',
}

DETAILS_URL_PATH = {
    'groups': '/api/3/action/group_show',
}


def get_requests_session(CKAN_API_KEY):
    CKAN_AUTH_HEADERS = {'Authorization': CKAN_API_KEY}
    session = requests.session()
    session.headers.update(CKAN_AUTH_HEADERS)
    return session


def parse_ckan_row(row, schema):
    output_row = {}
    for field in schema['fields']:
        value = row.get(field['name'], '')
        value = {
            'string': str,
            'integer': int,
            'datetime': lambda v: datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f'),
            'boolean': bool,
            'array': lambda v: v
        }[field['type']](value)
        output_row[field['name']] = value
    return output_row


def get(datapackage, resources, stats, session, url, obj_type, limit, delay_seconds):
    schema = SCHEMAS[obj_type]
    rows_per_page = ROWS_PER_PAGE.get(obj_type)
    request_data = INITIAL_REQUEST_DATA[obj_type]
    url_path = ACTION_URL_PATH[obj_type]
    stats['loaded {}'.format(obj_type)] = 0

    def __get_objs_page():
        logging.info('{url}{url_path} {request_data}'.format(url=url, url_path=url_path, request_data=request_data))
        get_res = session.post('{url}{url_path}'.format(url=url, url_path=url_path), data=request_data).json()
        assert get_res and get_res['success']
        return get_res['result']

    def __get():
        if rows_per_page:
            offset = 0
            while True:
                sleep(delay_seconds)
                request_data.update(limit=limit or rows_per_page, offset=offset)
                objs = __get_objs_page()
                num_objs = 0
                for num_objs, obj in enumerate(objs, 1):
                    yield parse_ckan_row(obj, schema)
                    stats['loaded {}'.format(obj_type)] += 1
                if num_objs == 0 or limit:
                    break
                offset += num_objs
        else:
            if limit:
                request_data.update(limit=limit)
            for obj in __get_objs_page():
                yield parse_ckan_row(obj, schema)
                stats['loaded {}'.format(obj_type)] += 1

    descriptor = {'name': 'ckan_{obj_type}'.format(obj_type=obj_type),
                  'path': 'ckan_{obj_type}.csv'.format(obj_type=obj_type), 'schema': schema,
                  PROP_STREAMING: True}
    rows_iter = __get()
    datapackage.setdefault('resources', []).append(descriptor)
    return datapackage, chain(resources, [rows_iter]), stats


def create(datapackage, resources, stats, session, url, obj_type, limit, delay_seconds):
    url_path = ACTION_URL_PATH['{}_create'.format(obj_type)]
    stats['num_created_{}s'.format(obj_type)] = 0

    def _create(rows):
        for i, row in enumerate(rows):
            if limit and i >= limit:
                continue
            logging.info('creating {}: {}'.format(obj_type, row))
            sleep(delay_seconds)
            create_res = session.post('{}{}'.format(url, url_path), data=row).json()
            assert create_res and create_res['success']
            yield row
            stats['num_created_{}s'.format(obj_type)] += 1

    return datapackage, (_create(rows) for rows in resources), stats


def _ckan(datapackage, resources, stats, action, obj_type, session, url, limit, delay_seconds):
    if action == 'get':
        if obj_type in ['group', 'groups', 'grp']:
            return get(datapackage, resources, stats, session, url, 'groups', limit, delay_seconds)
        elif obj_type in ['user', 'users', 'usr']:
            return get(datapackage, resources, stats, session, url, 'users', limit, delay_seconds)
        elif obj_type in ['organization', 'organizations', 'org']:
            return get(datapackage, resources, stats, session, url, 'organizations', limit, delay_seconds)
    elif action == 'create':
        if obj_type == 'member':
            return create(datapackage, resources, stats, session, url, 'member', limit, delay_seconds)
    raise NotImplementedError


def ckan(datapackage, resources, stats, action, obj_type, CKAN_API_KEY=None, CKAN_URL=None,
         limit=None, delay_seconds=.2):
    if not CKAN_API_KEY:
        CKAN_API_KEY = os.environ.get('CKAN_API_KEY')
    if not CKAN_URL:
        CKAN_URL = os.environ.get('CKAN_URL')
    assert CKAN_API_KEY and CKAN_URL
    return _ckan(datapackage, resources, stats, action, obj_type, get_requests_session(CKAN_API_KEY), CKAN_URL, int(limit) if limit else None, delay_seconds)


if __name__ == '__main__':
    parameters, datapackage, resources, stats = ingest() + ({},)
    descriptor, rows_iter, stats = ckan(datapackage, resources, stats, **parameters)
    for resource in descriptor.get('resources', []):
        resource[PROP_STREAMING] = True
    spew(descriptor, rows_iter, stats)
