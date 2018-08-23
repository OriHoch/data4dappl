import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.lib.plugins import DefaultTranslation
from .supersede_resource import toolkit_add_resource


class Odata_Org_IlPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit_add_resource('fanstatic', 'odata_org_il',
                             supersedes={'autocomplete.js': ('base',
                                                             'modules/autocomplete.js')})

    def i18n_domain(self):
        return 'ckan'

    def get_homepage_datasets(self, *args, **kwargs):
        psearch = toolkit.get_action("package_search")
        psearch_ret = psearch(data_dict={"sort":"metadata_modified desc","rows":5})
        results = psearch_ret['results']
        return results
        # result_str_list = [ "Name: %(name)s<br>Notes: %(notes)s<br>Created:%(metadata_created)s<br>Modified:%(metadata_modified)s<br>URL:%(url)s" % entry for entry in results ]
        # return "<br>".join(result_str_list)

    # Tell CKAN what custom template helper functions this plugin provides,
    # see the ITemplateHelpers plugin interface.
    def get_helpers(self):
        return {'homepage_datasets': self.get_homepage_datasets}

