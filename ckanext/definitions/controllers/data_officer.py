import ckan.lib.base as base
import ckan.model as model
import ckan.authz as authz
import ckanext.user_extra.logic.action.get as get
import logging
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
import ckan.lib.navl.dictization_functions as dict_fns
from ckan.common import OrderedDict
import ckan.logic as logic
from six import string_types
from urllib import urlencode
import ckan.lib.search as search
import ckan.lib.helpers as h
import ckan.plugins as plugins

import ckanext.definitions.model.definition as definition_model

tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params

log = logging.getLogger(__name__)
abort = base.abort


class DataOfficerController(base.BaseController):

    def index(self):
        context = {'model': model, 'session': model.Session,
                   'user': toolkit.c.user}

        try:
            toolkit.check_access('data_officer_read', context)
        except toolkit.NotAuthorized:
            abort(403, toolkit._('Unauthorized to see data officers %s') % '')

        data_officer_list = toolkit.get_action('data_officer_list')(context, {})

        extra_vars = {'data_officer_list': data_officer_list}

        return toolkit.render('data_officer/index.html', extra_vars=extra_vars)


    def edit(self):
        context = {'model': model, 'session': model.Session,
                   'user': toolkit.c.user}

        try:
            toolkit.check_access('data_officer_manage', context)
        except toolkit.NotAuthorized:
            abort(403, toolkit._('Unauthorized to manage data officer %s') % '')

        data_officer_list = toolkit.get_action('data_officer_list')(context, {})

        extra_vars = {'data_officer_list': data_officer_list}

        return toolkit.render('data_officer/edit.html', extra_vars=extra_vars)


    def new(self):
        context = {'model': model, 'session': model.Session,
                   'user': toolkit.c.user}


        try:
            toolkit.check_access('data_officer_create', context)
        except toolkit.NotAuthorized:
            abort(403, toolkit._('Unauthorized to create data officer %s') % '')


        user_id = toolkit.get_converter('convert_user_name_or_id_to_id')\
            (toolkit.request.params.get('user_id', None), context)


        log.info('user_id = {0}'.format(user_id))

        data_dict = {'user_id': user_id}
        toolkit.get_action('data_officer_create')(context, data_dict)

        return toolkit.redirect_to('data_officer_edit')


    def delete(self, user_id):
        context = {'model': model, 'session': model.Session,
                   'user': toolkit.c.user}

        try:
            toolkit.check_access('data_officer_delete', context)
        except toolkit.NotAuthorized:
            abort(403, toolkit._('Unauthorized to delete data officer %s') % '')

        data_dict = {'user_id': user_id}
        toolkit.get_action('data_officer_delete')(context, data_dict)

        return toolkit.redirect_to('data_officer_edit')


