def deploy_resource(resource):
    client = get_client(resource)
    resource_type = get_resource_type(resource)
    func_details = RESOURCE_TO_FUNCTION.get(resource_type)
    if not func_details:
        LOGGER.warning('Resource type not yet implemented: %s' % resource['Type'])
        return
    func_details = func_details[ACTION_CREATE]
    function = getattr(client, func_details['function'])
    params = dict(func_details['parameters'])
    if 'Properties' not in resource:
        resource['Properties'] = {}
    for param_key, prop_key in iteritems(params):
        params[param_key] = resource['Properties'].get(prop_key)
    # invoke function
    return function(**params)