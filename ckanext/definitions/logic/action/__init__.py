from ckan import model
from ckan.lib.search import index_for
from ckan.plugins import toolkit
import logging
from ckanext.definitions.model import Definition
from model import Activity

log = logging.getLogger(__name__)

PACKAGE_INDEX = index_for(model.Package)


def reindex_package(package_id, defer_commit=False):
    log.info("reindex_package :: package_id = {}".format(package_id))
    context = {'model': model, 'ignore_auth': True, 'validate': False, 'use_cache': False}
    pkg_dict = toolkit.get_action('package_show')(context, {'id': package_id})
    PACKAGE_INDEX.update_dict(pkg_dict, defer_commit=defer_commit)
    return pkg_dict


def reindex_packages(package_ids, defer_commit=False):
    pkg_dicts = [reindex_package(package_id, True) for package_id in package_ids]
    if not defer_commit:
        PACKAGE_INDEX.commit()
    return pkg_dicts


def create_definition_package_relationship_activities(
    session, package, definition, user_name, activity_type
):

    assert activity_type in ('added', 'removed')

    user_obj = model.User.by_name(user_name)
    if user_obj:
        user_id = user_obj.id
    else:
        user_id = 'not logged in'

    dictized_package = toolkit.get_action('package_show')({
        'model': model,
        'session': session,
        'for_view': False,  # avoid ckanext-multilingual translating it
        'ignore_auth': True
    }, {
        'id': package.id,
        'include_tracking': False
    })
    package_activity = Activity(
        user_id=user_id,
        object_id=package.id,
        activity_type="{} definition".format(activity_type),
        data={
            'package': dictized_package,
            'definition': {
                'title': [definition.id, definition.display_name]
            },
            'actor': user_obj.name if user_obj else None
        }
    )
    session.add(package_activity)

    dictized_definition = toolkit.get_action('definition_show')({
        'model': model,
        'session': session,
        'for_view': False,  # avoid ckanext-multilingual translating it
        'ignore_auth': True
    }, {
        'id': definition.id
    })
    dictized_definition['title'] = dictized_definition['display_name']
    definition_activity = Activity(
        user_id=user_id,
        object_id=definition.id,
        activity_type="{} package".format(activity_type),
        data={
            'package': {
                'title': [package.id, package.title, package.type]
            },
            'definition': dictized_definition,
            'actor': user_obj.name if user_obj else None
        }
    )
    session.add(definition_activity)
