from datapackage_pipelines_ckan.processors.add_ckan_resource import AddCkanResource
from datapackage_pipelines_ckanext import helpers as ckanext_helpers
from functools import lru_cache
from os import environ


@lru_cache()
def get_config(key):
    return ckanext_helpers.get_plugin_configuration('odata_org_il').get(key)


class AddCkanFoiGroupsMatchingResource(AddCkanResource):

    def get_parameters(self, parameters):
        parameters['resource-id'] = get_config('foi_groups_matching_resource_id')
        super(AddCkanFoiGroupsMatchingResource, self).get_parameters(parameters)

    def update_ckan_resource(self, resource):
        super(AddCkanFoiGroupsMatchingResource, self).update_ckan_resource(resource)
        resource.update(http_headers={'Authorization': environ['CKAN_API_KEY']},
                        name='foi-groups-matching', path='foi-groups-matching.csv')


if __name__ == '__main__':
    AddCkanFoiGroupsMatchingResource()()
