def deploy_template(template):
    if isinstance(template, string_types):
        template = parse_template(template)

    for key, resource in iteritems(template['Resources']):
        deploy_resource(resource)