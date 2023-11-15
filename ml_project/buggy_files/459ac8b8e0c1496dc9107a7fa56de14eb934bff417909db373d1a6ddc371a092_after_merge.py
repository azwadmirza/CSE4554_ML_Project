def list_policy_assignment(cmd, disable_scope_strict_match=None, resource_group_name=None, scope=None):
    from azure.cli.core.commands.client_factory import get_subscription_id
    policy_client = _resource_policy_client_factory(cmd.cli_ctx)
    _scope = _build_policy_scope(get_subscription_id(cmd.cli_ctx),
                                 resource_group_name, scope)
    id_parts = parse_resource_id(_scope)
    subscription = id_parts.get('subscription')
    resource_group = id_parts.get('resource_group')
    resource_type = id_parts.get('child_type_1') or id_parts.get('type')
    resource_name = id_parts.get('child_name_1') or id_parts.get('name')

    if all([resource_type, resource_group, subscription]):
        namespace = id_parts.get('namespace')
        parent_resource_path = '' if not id_parts.get('child_name_1') else (id_parts['type'] + '/' + id_parts['name'])
        result = policy_client.policy_assignments.list_for_resource(
            resource_group, namespace,
            parent_resource_path, resource_type, resource_name)
    elif resource_group:
        result = policy_client.policy_assignments.list_for_resource_group(resource_group)
    elif subscription:
        result = policy_client.policy_assignments.list()
    elif scope:
        raise CLIError('usage error `--scope`: must be a fully qualified ARM ID.')
    else:
        raise CLIError('usage error: --scope ARM_ID | --resource-group NAME | --subscription ID')

    if not disable_scope_strict_match:
        result = [i for i in result if _scope.lower() == i.scope.lower()]

    return result