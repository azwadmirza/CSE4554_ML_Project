def acr_credential_show(cmd, client, registry_name, resource_group_name=None):
    return get_acr_credentials(cmd.cli_ctx, client, registry_name, resource_group_name)