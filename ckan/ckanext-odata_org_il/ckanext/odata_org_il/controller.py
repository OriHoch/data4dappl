import ckan.plugins as p
from ckan.controllers.group import GroupController, model, NotAuthorized, abort, c, render, request, NotFound, get_action
import json


def _related_groups_iterator(context, groups, source_group_name):
    for group in groups:
        if group['name'] == source_group_name: continue
        data_dict = {
            'q': '',
            'fq': 'groups:"%s"' % group['name'],
            'include_private': False,
            'facet.limit': -1,
            'facet.field': ['groups'],
            'rows': 0
        }
        yield {
            'name': group['name'],
            'display_name': group['display_name'],
            'num_datasets': group['count'],
            'num_related_groups': len(get_action('package_search')(context, data_dict)['search_facets']['groups']['items'])
        }


class GroupEntitiesController(GroupController):

    def show_entities(self):
        id = request.params.get('name', '')
        _ = self._ensure_controller_matches_group_type(id)
        context = {'model': model, 'session': model.Session,
                   'user': c.user}
        c.group_dict = self._get_group_dict(id, include_datasets=True)
        group_type = c.group_dict['type']
        self._setup_template_variables(context, {'id': id},
                                       group_type=group_type)
        context = {'model': model, 'session': model.Session,
                   'user': c.user,
                   'for_view': True, 'extras_as_string': True,
                   'return_query': True}
        q = ''
        if c.group_dict.get('is_organization'):
            fq = 'owner_org:"%s"' % c.group_dict.get('id')
        else:
            fq = 'groups:"%s"' % c.group_dict.get('name')
        data_dict = {
            'q': q,
            'fq': fq,
            'include_private': False,
            'facet.limit': -1,
            'facet.field': ['groups'],
            'rows': 0
        }
        query = get_action('package_search')(context, data_dict)
        c.entities_extras = []
        c.query = query
        for item in query['search_facets']['groups']['items']:
            c.entities_extras.append({'key': item['display_name'], 'value': item['count']})

        return render('group/entities.html',
                      extra_vars={'group_type': group_type, 'json': json})

    def show_entities_api(self):
        id = request.params.get('name', '')
        _ = self._ensure_controller_matches_group_type(id)
        context = {'model': model, 'session': model.Session,
                   'user': c.user}
        c.group_dict = self._get_group_dict(id, include_datasets=True)
        group_type = c.group_dict['type']
        self._setup_template_variables(context, {'id': id},
                                       group_type=group_type)
        context = {'model': model, 'session': model.Session,
                   'user': c.user,
                   'for_view': True, 'extras_as_string': True,
                   'return_query': True}
        q = ''
        if c.group_dict.get('is_organization'):
            fq = 'owner_org:"%s"' % c.group_dict.get('id')
        else:
            fq = 'groups:"%s"' % c.group_dict.get('name')
        data_dict = {
            'q': q,
            'fq': fq,
            'include_private': False,
            'facet.limit': -1,
            'facet.field': ['groups'],
            'rows': 0
        }
        query = get_action('package_search')(context, data_dict)
        c.entities_extras = []
        c.query = query
        from ckan.common import response
        response.headers['Content-type'] = 'application/json; charset=utf-8'
        response.headers['Access-Control-Allow-Origin'] = '*'
        group = {}
        for extra in c.group_dict['extras']:
            group[extra['key']] = extra['value']
        for k, v in c.group_dict.items():
            if k not in ['users', 'extras', 'packages']:
                group[k] = v
        return json.dumps({
            'group': group,
            'related_groups': list(_related_groups_iterator(context, query['search_facets']['groups']['items'], group['name']))
        }, ensure_ascii=False, indent=2)

    def _get_group_dict(self, id, include_datasets=False):
        context = {'model': model, 'session': model.Session,
                   'user': c.user,
                   'for_view': True}
        try:
            return self._action('group_show')(
                context, {'id': id, 'include_datasets': include_datasets})
        except (NotFound, NotAuthorized):
            abort(404, _('Group not found'))
