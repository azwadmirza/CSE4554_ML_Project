def list_deleted_vault_or_hsm(cmd, client, resource_type=None):
    if is_azure_stack_profile(cmd):
        return client.list_deleted()

    if resource_type is None:
        hsm_client = get_client_factory(ResourceType.MGMT_KEYVAULT, Clients.managed_hsms)(cmd.cli_ctx, None)
        deleted_resources = []
        try:
            deleted_resources.extend(client.list_deleted())
            deleted_resources.extend(hsm_client.list_deleted())
        except:  # pylint: disable=bare-except
            pass

        return deleted_resources

    if resource_type == 'hsm':
        hsm_client = get_client_factory(ResourceType.MGMT_KEYVAULT, Clients.managed_hsms)(cmd.cli_ctx, None)
        return hsm_client.list_deleted()

    if resource_type == 'vault':
        return client.list_deleted()

    raise CLIError('Unsupported resource type: {}'.format(resource_type))