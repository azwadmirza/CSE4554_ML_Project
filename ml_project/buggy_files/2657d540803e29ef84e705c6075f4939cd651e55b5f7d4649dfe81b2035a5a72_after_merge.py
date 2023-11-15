def _get_vault_id_from_name(cli_ctx, client, vault_name):
    group_name = _get_resource_group_from_vault_name(cli_ctx, vault_name)
    if not group_name:
        raise CLIError("unable to find vault '{}' in current subscription.".format(vault_name))
    vault = client.get(group_name, vault_name)
    return vault.id