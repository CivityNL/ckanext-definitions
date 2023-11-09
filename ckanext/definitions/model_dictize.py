# encoding: utf-8

'''
These dictize functions generally take a domain object (such as Package) and
convert it to a dictionary, including related objects (e.g. for Package it
includes PackageTags, PackageExtras, PackageGroup etc).

The basic recipe is to call:

    dictized = ckan.lib.dictization.table_dictize(domain_object)

which builds the dictionary by iterating over the table columns.
'''

import ckan.lib.dictization as dictization


def definition_dictize(definition, context):
    result = None
    if context.get('with_capacity'):
        definition, capacity = definition
        result = dictization.table_dictize(definition, context, capacity=capacity)
    else:
        result = dictization.table_dictize(definition, context)
    return result


def definition_list_dictize(definition_list, context):
    return [definition_dictize(definition, context) for definition in definition_list]
