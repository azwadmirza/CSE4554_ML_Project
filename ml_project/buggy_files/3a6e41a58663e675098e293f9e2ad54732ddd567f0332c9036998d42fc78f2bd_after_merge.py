def _get_resource_id(cli_ctx, val, resource_group, resource_type, resource_namespace):
    from msrestazure.tools import resource_id, is_valid_resource_id
    from azure.cli.core.commands.client_factory import get_subscription_id
    if is_valid_resource_id(val):
        return val

    kwargs = {
        'name': val,
        'resource_group': resource_group,
        'namespace': resource_namespace,
        'type': resource_type,
        'subscription': get_subscription_id(cli_ctx)
    }
    missing_kwargs = {k: v for k, v in kwargs.items() if not v}

    return resource_id(**kwargs) if not missing_kwargs else None