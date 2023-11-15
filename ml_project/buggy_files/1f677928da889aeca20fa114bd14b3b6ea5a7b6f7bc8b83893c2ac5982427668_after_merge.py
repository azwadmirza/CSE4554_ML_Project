def merge_service_dicts(base, override, version):
    md = MergeDict(base, override)

    md.merge_mapping('environment', parse_environment)
    md.merge_mapping('labels', parse_labels)
    md.merge_mapping('ulimits', parse_ulimits)
    md.merge_mapping('networks', parse_networks)
    md.merge_sequence('links', ServiceLink.parse)

    for field in ['volumes', 'devices']:
        md.merge_field(field, merge_path_mappings)

    for field in [
        'ports', 'cap_add', 'cap_drop', 'expose', 'external_links',
        'security_opt', 'volumes_from', 'depends_on',
    ]:
        md.merge_field(field, merge_unique_items_lists, default=[])

    for field in ['dns', 'dns_search', 'env_file', 'tmpfs']:
        md.merge_field(field, merge_list_or_string)

    md.merge_field('logging', merge_logging, default={})

    for field in set(ALLOWED_KEYS) - set(md):
        md.merge_scalar(field)

    if version == V1:
        legacy_v1_merge_image_or_build(md, base, override)
    elif md.needs_merge('build'):
        md['build'] = merge_build(md, base, override)

    return dict(md)