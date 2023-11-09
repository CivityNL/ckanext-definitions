import ckan.lib.base as base
import ckan.model as model
import logging
import ckan.plugins.toolkit as toolkit

import ckan.logic as logic

tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params

_ = toolkit._

log = logging.getLogger(__name__)
abort = base.abort


def _get_context():
    return {'model': model, 'session': model.Session, 'user': toolkit.c.user}


def index():
    context = _get_context()

    try:
        toolkit.check_access('data_officer_read', context)
    except toolkit.NotAuthorized:
        abort(403, _('Unauthorized to see data officers %s') % '')

    data_officer_list = toolkit.get_action('data_officer_list')(context, {})
    extra_vars = {'data_officer_list': data_officer_list}
    return toolkit.render('data_officer/index.html', extra_vars=extra_vars)


def edit():
    context = _get_context()

    try:
        toolkit.check_access('data_officer_manage', context)
    except toolkit.NotAuthorized:
        abort(403, _('Unauthorized to manage data officer %s') % '')

    data_officer_list = toolkit.get_action('data_officer_list')(context, {})
    extra_vars = {'data_officer_list': data_officer_list}
    return toolkit.render('data_officer/edit.html', extra_vars=extra_vars)


def new():
    context = _get_context()
    user_id = toolkit.get_or_bust(toolkit.request.values, 'user_id')

    try:
        toolkit.check_access('data_officer_create', context)
    except toolkit.NotAuthorized:
        abort(403, _('Unauthorized to create data officers'))

    try:
        user_id = toolkit.get_converter('convert_user_name_or_id_to_id')(user_id, context)
    except toolkit.Invalid:
        toolkit.redirect_to('data_officer.edit')
    except toolkit.ObjectNotFound:
        toolkit.redirect_to('data_officer.edit')

    data_dict = {'user_id': user_id}
    toolkit.get_action('data_officer_create')(context, data_dict)

    return toolkit.redirect_to('data_officer.edit')


def delete(user_id):
    context = _get_context()

    try:
        toolkit.check_access('data_officer_delete', context)
    except toolkit.NotAuthorized:
        abort(403, _('Unauthorized to delete data officer %s') % '')

    data_dict = {'user_id': user_id}
    toolkit.get_action('data_officer_delete')(context, data_dict)
    return toolkit.redirect_to('data_officer.edit')
