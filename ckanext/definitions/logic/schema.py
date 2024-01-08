from ckan.logic.schema import validator_args


@validator_args
def default_definitions_schema(
        not_missing, not_empty, unicode_safe, tag_length_validator,
        tag_name_validator, ignore_missing, vocabulary_id_exists,
        ignore):
    return {
        'name': [not_missing,
                 not_empty,
                 unicode_safe,
                 tag_length_validator,
                 tag_name_validator,
                 ],
        'vocabulary_id': [ignore_missing,
                          unicode_safe,
                          vocabulary_id_exists],
        'revision_timestamp': [ignore],
        'state': [ignore],
        'display_name': [ignore],
    }


@validator_args
def default_create_definitions_schema(
        not_missing, not_empty, unicode_safe, vocabulary_id_exists,
        tag_not_in_vocabulary, empty):
    schema = default_definitions_schema()
    # When creating a tag via the tag_create() logic action function, a
    # vocabulary_id _must_ be given (you cannot create free tags via this
    # function).
    schema['vocabulary_id'] = [not_missing, not_empty, unicode_safe,
                               vocabulary_id_exists, tag_not_in_vocabulary]
    # You're not allowed to specify your own ID when creating a tag.
    schema['id'] = [empty]
    return schema


@validator_args
def default_update_definitions_schema(
        not_missing, not_empty, unicode_safe, vocabulary_id_exists,
        tag_not_in_vocabulary, empty):
    schema = default_definitions_schema()
    # When creating a tag via the tag_create() logic action function, a
    # vocabulary_id _must_ be given (you cannot create free tags via this
    # function).
    schema['vocabulary_id'] = [not_missing, not_empty, unicode_safe,
                               vocabulary_id_exists, tag_not_in_vocabulary]
    # You're not allowed to specify your own ID when creating a tag.
    schema['id'] = [empty]
    return schema
