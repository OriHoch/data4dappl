import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultTranslation
import random


class Odata_Org_IlPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config):
        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('fanstatic', 'odata_org_il')

    def i18n_domain(self):
        return 'ckan'

    def get_homepage_datasets(self, *args, **kwargs):
        psearch = toolkit.get_action("package_search")
        psearch_ret = psearch(data_dict={"sort":"metadata_modified desc",
                                         "rows":5})
        results = psearch_ret['results']
        return results
        # result_str_list = [ "Name: %(name)s<br>Notes: %(notes)s<br>Created:%(metadata_created)s<br>Modified:%(metadata_modified)s<br>URL:%(url)s" % entry for entry in results ]
        # return "<br>".join(result_str_list)

    def get_homepage_tags(self, *args, **kwargs):
        psearch = toolkit.get_action("package_search")
        psearch_ret = psearch(data_dict={'facet.field': ['tags'],
                                         'facet.limit': 30,
                                         'rows': 0})
        tags = psearch_ret['search_facets']['tags']['items']
        return random.sample(filter(lambda t: t['count'] > 20, tags), 5)

    # Tell CKAN what custom template helper functions this plugin provides,
    # see the ITemplateHelpers plugin interface.
    def get_helpers(self):
        return {'homepage_datasets': self.get_homepage_datasets,
                'homepage_tags': self.get_homepage_tags}

