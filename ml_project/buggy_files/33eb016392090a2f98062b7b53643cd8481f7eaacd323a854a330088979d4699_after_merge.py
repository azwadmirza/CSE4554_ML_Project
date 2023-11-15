def acr_credential_show(cmd, client, registry_name, resource_group_name=None):
    registry, resource_group_name = get_registry_by_name(cmd.cli_ctx, registry_name, resource_group_name)

    if registry.admin_user_enabled:  # pylint: disable=no-member
        return client.list_credentials(resource_group_name, registry_name)

    admin_not_enabled_error(registry_name)