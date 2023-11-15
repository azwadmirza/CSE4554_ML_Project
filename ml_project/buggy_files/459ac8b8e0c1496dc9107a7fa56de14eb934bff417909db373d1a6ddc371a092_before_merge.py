def list_policy_assignment(cmd, disable_scope_strict_match=None, resource_group_name=None, scope=None):
    policy_client = _resource_policy_client_factory(cmd.cli_ctx)
    if scope and not is_valid_resource_id(scope):
        parts = scope.strip('/').split('/')
        if len(parts) == 4:
            resource_group_name = parts[3]
        elif len(parts) == 2:
            # rarely used, but still verify
            if parts[1].lower() != policy_client.config.subscription_id.lower():
                raise CLIError("Please use current active subscription's id")
        else:
            err = "Invalid scope '{}', it should point to a resource group or a resource"
            raise CLIError(err.format(scope))
        scope = None

    _scope = _build_policy_scope(policy_client.config.subscription_id,
                                 resource_group_name, scope)
    if resource_group_name:
        result = policy_client.policy_assignments.list_for_resource_group(resource_group_name)
    elif scope:
        # pylint: disable=redefined-builtin
        id = parse_resource_id(scope)
        parent_resource_path = '' if not id.get('child_name_1') else (id['type'] + '/' + id['name'])
        resource_type = id.get('child_type_1') or id['type']
        resource_name = id.get('child_name_1') or id['name']
        result = policy_client.policy_assignments.list_for_resource(
            id['resource_group'], id['namespace'],
            parent_resource_path, resource_type, resource_name)
    else:
        result = policy_client.policy_assignments.list()

    if not disable_scope_strict_match:
        result = [i for i in result if _scope.lower() == i.scope.lower()]

    return result