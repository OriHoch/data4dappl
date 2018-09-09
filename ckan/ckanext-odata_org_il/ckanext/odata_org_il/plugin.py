import ckan.plugins as plugins
from ckan.plugins.toolkit import (add_template_directory, add_public_directory, add_resource,
                                  get_action)
from ckan.lib.plugins import DefaultTranslation
import random
from .feed_middleware import FeedMiddleware


class Odata_Org_IlPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IMiddleware)

    def update_config(self, config):
        add_template_directory(config, 'templates')
        add_public_directory(config, 'public')
        add_resource('fanstatic', 'odata_org_il')

    def i18n_domain(self):
        return 'ckanext-odata_org_il'

    def get_homepage_datasets(self, *args, **kwargs):
        psearch = get_action("package_search")
        psearch_ret = psearch(data_dict={"sort":"metadata_modified desc",
                                         "rows":5})
        results = psearch_ret['results']
        return results
        # result_str_list = [ "Name: %(name)s<br>Notes: %(notes)s<br>Created:%(metadata_created)s<br>Modified:%(metadata_modified)s<br>URL:%(url)s" % entry for entry in results ]
        # return "<br>".join(result_str_list)

    def get_homepage_tags(self, *args, **kwargs):
        try:
            psearch = get_action("package_search")
            psearch_ret = psearch(data_dict={'facet.field': ['tags'],
                                             'facet.limit': 30,
                                             'rows': 0})
            tags = psearch_ret['search_facets']['tags']['items']
            return random.sample(filter(lambda t: t['count'] > 20, tags), 5)
        except Exception:
            return []

    # Tell CKAN what custom template helper functions this plugin provides,
    # see the ITemplateHelpers plugin interface.
    def get_helpers(self):
        return {'homepage_datasets': self.get_homepage_datasets,
                'homepage_tags': self.get_homepage_tags}

    def make_middleware(self, app, config):
        from ckan.config.middleware.flask_app import CKANFlask
        if isinstance(app, CKANFlask):
            app.wsgi_app = FeedMiddleware(app.wsgi_app)
        return app

    def make_error_log_middleware(self, app, config):
        return app
