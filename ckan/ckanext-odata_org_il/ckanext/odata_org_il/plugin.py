import ckan.plugins as plugins
from ckan.plugins.toolkit import (add_template_directory, add_public_directory, add_resource,
                                  get_action, url_for, config)
from ckan.lib.plugins import DefaultTranslation
import random
from .feed_middleware import FeedMiddleware
from ckan.controllers.feed import _FixedAtom1Feed
from ckanext.datapackage_pipelines.interfaces import IDatapackagePipelines
import os


class FeedClass(_FixedAtom1Feed):

    def _fix_link(self, link):
        if 'action/package_read?id=' in link:
            pkg_id = link.split('=')[1]
            return config.get('ckan.site_url') + url_for(controller='package', action='read', id=pkg_id)

    def add_item(self, *args, **kwargs):
        if 'link' in kwargs:
            kwargs['link'] = self._fix_link(kwargs['link'])
        super(FeedClass, self).add_item(*args, **kwargs)


# def group_entities(id):
#     group_show = toolkit.get_action('group_show')
#     this ensures current user is authorized to view the group
    # group = group_show(data_dict={'name_or_id': id})
    # assert group
    # return str(group)

class Odata_Org_IlPlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.ITranslation)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IMiddleware)
    plugins.implements(plugins.IFeed)
    plugins.implements(IDatapackagePipelines)
    plugins.implements(plugins.IRoutes, inherit=True)

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

    def get_feed_class(self):
        return FeedClass

    def get_item_additional_fields(self, dataset_dict):
        return {}

    def register_pipelines(self):
        return 'ckanext-odata_org_il', os.path.join(os.path.dirname(__file__), 'pipelines')

    def get_pipelines_config(self):
        return {'foi_groups_matching_resource_id': config.get('ckanext.odata_org_il.foi_groups_matching_resource_id')}

    def before_map(self, m):
        m.connect('group_entities',  # name of path route
                  '/group/entities',  # url to map path to
                  controller='ckanext.odata_org_il.controller:GroupEntitiesController',  # controller
                  action='show_entities')  # controller action (method)
        m.connect('group_entities_api',  # name of path route
                  '/group/entities/api',  # url to map path to
                  controller='ckanext.odata_org_il.controller:GroupEntitiesController',  # controller
                  action='show_entities_api')  # controller action (method)
        return m
