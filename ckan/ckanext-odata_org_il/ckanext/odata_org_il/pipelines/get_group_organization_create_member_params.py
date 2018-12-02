from datapackage_pipelines.utilities.resources import PROP_STREAMING
from datapackage_pipelines.wrapper import ingest, spew


def get_group_users_to_create(entities, all_organization_user_ids):
    for entity in entities:
        entity_user_ids = [entity_user['id'] for entity_user in entity['users']]
        for organiztion_user_id in all_organization_user_ids:
            if organiztion_user_id not in entity_user_ids:
                yield {'object': organiztion_user_id,
                       'object_type': 'user',
                       'id': entity['id'],
                       'capacity': 'member'}


def get_create_member_params(datapackage, resources, stats):
    resource_names = [resource['name'] for resource in datapackage.get('resources', [])]
    datapackage['resources'] = [{"name": "group_users_to_create", "path": "group_users_to_create.csv",
                                 PROP_STREAMING: True,
                                 "schema": {"fields": [{"name": "id", "type": "string"},
                                                       {"name": "object", "type": "string"},
                                                       {"name": "object_type", "type": "string"},
                                                       {"name": "capacity", "type": "string"}]}}]

    def _get_params():
        all_organization_user_ids = set()
        for resource_name, rows in zip(resource_names, resources):
            if resource_name == 'ckan_organizations':
                for org in rows:
                    for org_user in org['users']:
                        all_organization_user_ids.add(org_user['id'])
            elif resource_name == 'ckan_groups':
                yield get_group_users_to_create(rows, all_organization_user_ids)
            else:
                raise Exception()

    return datapackage, _get_params(), stats

if __name__ == '__main__':
    parameters, datapackage, resources = ingest()
    datapackage, resources, stats = get_create_member_params(datapackage, resources, {})
    spew(datapackage, resources, stats)
