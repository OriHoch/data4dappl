import ckan.plugins as p
from ckan.controllers.group import GroupController, model, NotAuthorized, abort, c, render, request, NotFound, get_action
import json


class GroupEntitiesController(GroupController):

    def show_entities(self):
        id = request.params.get('id', '')
        group_type = self._ensure_controller_matches_group_type(id)
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

    def _get_group_dict(self, id, include_datasets=False):
        context = {'model': model, 'session': model.Session,
                   'user': c.user,
                   'for_view': True}
        try:
            return self._action('group_show')(
                context, {'id': id, 'include_datasets': include_datasets})
        except (NotFound, NotAuthorized):
            abort(404, _('Group not found'))
