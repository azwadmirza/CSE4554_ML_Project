def deploy_resource(resource_id, resources, stack_name):
    resource = resources[resource_id]
    client = get_client(resource)
    if not client:
        return False
    resource_type = get_resource_type(resource)
    func_details = RESOURCE_TO_FUNCTION.get(resource_type)
    if not func_details:
        LOGGER.warning('Resource type not yet implemented: %s' % resource['Type'])
        return
    func_details = func_details[ACTION_CREATE]
    function = getattr(client, func_details['function'])
    params = dict(func_details['parameters'])
    defaults = func_details.get('defaults', {})
    if 'Properties' not in resource:
        resource['Properties'] = {}
    # print('deploying', resource_id, resource_type)
    for param_key, prop_keys in iteritems(dict(params)):
        params.pop(param_key, None)
        if not isinstance(prop_keys, list):
            prop_keys = [prop_keys]
        for prop_key in prop_keys:
            if prop_key == PLACEHOLDER_RESOURCE_NAME:
                # obtain physical resource name from stack resources
                params[param_key] = resolve_ref(stack_name, resource_id, resources,
                    attribute='PhysicalResourceId')
            else:
                prop_value = resource['Properties'].get(prop_key)
                if prop_value is not None:
                    params[param_key] = prop_value
            tmp_value = params.get(param_key)
            if tmp_value is not None:
                params[param_key] = resolve_refs_recursively(stack_name, tmp_value, resources)
                break
        # hack: convert to boolean
        if params.get(param_key) in ['True', 'False']:
            params[param_key] = params.get(param_key) == 'True'
    # assign default value if empty
    params = common.merge_recursive(defaults, params)
    # invoke function
    try:
        result = function(**params)
    except Exception as e:
        LOGGER.warning('Error calling %s with params: %s for resource: %s' % (function, params, resource))
        raise e
    # update status
    set_status_deployed(resource_id, resource, stack_name)
    return result