def template_settings(es_version, ecs_version, mappings_section, template_settings_file):
    if template_settings_file:
        with open(template_settings_file) as f:
            template = json.load(f)
    else:
        template = default_template_settings(ecs_version)

    if es_version == 6:
        mappings_section = copy.deepcopy(mappings_section)
        es6_type_fallback(mappings_section['properties'])

        # error.stack_trace needs special handling to set
        # index: false and doc_values: false if the field
        # is present in the mappings
        try:
            error_stack_trace_mappings = mappings_section['properties']['error']['properties']['stack_trace']
            error_stack_trace_mappings.setdefault('index', False)
            error_stack_trace_mappings.setdefault('doc_values', False)
        except KeyError:
            pass

        template['mappings'] = {'_doc': mappings_section}
    else:
        template['mappings'] = mappings_section

    # _meta can't be at template root in legacy templates, so moving back to mappings section
    # if present
    if '_meta' in template:
        mappings_section['_meta'] = template.pop('_meta')

    return template