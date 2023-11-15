def purge_vault_or_hsm(cmd, client, location=None, vault_name=None, hsm_name=None, no_wait=False):
    if is_azure_stack_profile(cmd) or vault_name:
        return sdk_no_wait(
            no_wait,
            client.begin_purge_deleted,
            location=location,
            vault_name=vault_name
        )

    assert hsm_name
    hsm_client = get_client_factory(ResourceType.MGMT_KEYVAULT, Clients.managed_hsms)(cmd.cli_ctx, None)
    return hsm_client.purge_deleted(rlocation=location, name=hsm_name)