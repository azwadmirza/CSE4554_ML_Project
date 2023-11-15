def db_to_form_package_schema():
    schema = default_package_schema()

    schema.update({
        'tags': {
            '__extras': [ckan.lib.navl.validators.keep_extras,
                ckan.logic.converters.free_tags_only]
            },
        })

    schema['resources'].update({
        'created': [ckan.lib.navl.validators.ignore_missing],
        'position': [not_empty],
        'last_modified': [ckan.lib.navl.validators.ignore_missing],
        'cache_last_updated': [ckan.lib.navl.validators.ignore_missing],
        'webstore_last_updated': [ckan.lib.navl.validators.ignore_missing],
        'revision_timestamp': [],
        'resource_group_id': [],
        'cache_last_updated': [],
        'webstore_last_updated': [],
        'size': [],
        'state': [],
        'last_modified': [],
        'mimetype': [],
        'cache_url': [],
        'name': [],
        'webstore_url': [],
        'mimetype_inner': [],
        'resource_type': [],
    })

    schema.update({
        'state': [ckan.lib.navl.validators.ignore_missing],
        'isopen': [ignore_missing],
        'license_url': [ignore_missing],
        })

    schema['groups'].update({
        'description': [ignore_missing],
        })

    # Remove validators for several keys from the schema so validation doesn't
    # strip the keys from the package dicts if the values are 'missing' (i.e.
    # None).
    schema['author'] = []
    schema['author_email'] = []
    schema['maintainer'] = []
    schema['maintainer_email'] = []
    schema['license_id'] = []
    schema['notes'] = []
    schema['url'] = []
    schema['version'] = []

    # Add several keys that are missing from default_package_schema(), so
    # validation doesn't strip the keys from the package dicts.
    #schema['license_title'] = []
    schema['metadata_created'] = []
    schema['metadata_modified'] = []
    schema['num_resources'] = []
    schema['num_tags'] = []
    schema['organization'] = []
    schema['owner_org'] = []
    schema['private'] = []
    schema['revision_id'] = []
    schema['revision_timestamp'] = []
    schema['tracking_summary'] = []
    schema['license_title'] = []

    return schema