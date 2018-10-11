from os import path, environ
import requests
from dataflows import Flow, load
from datapackage_pipelines_ckanext.helpers import get_plugin_configuration


config = get_plugin_configuration('odata_org_il')
data_path = config['data_path']

CKAN_API_KEY = environ.get('CKAN_API_KEY')
CKAN_URL = environ.get('CKAN_URL')
assert CKAN_API_KEY and CKAN_URL
CKAN_AUTH_HEADERS = {'Authorization': CKAN_API_KEY}
session = requests.session()
session.headers.update(CKAN_AUTH_HEADERS)


def restore_group_datasets(row):
    group_id = row['group_id']
    for dataset_id in row['dataset_ids']:
        res = session.post('{}/api/3/action/member_create'.format(CKAN_URL),
                           json=dict(id=group_id,
                                     object=dataset_id,
                                     object_type='package',
                                     capacity='')).json()
        assert res and res['success']


Flow(
    load(path.join(data_path, 'dump_group_datasets/datapackage.json'), resources=['group_datasets']),
    restore_group_datasets
).process()
