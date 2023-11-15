def purge_vault_or_hsm(cmd, client, location=None, vault_name=None, hsm_name=None,  # pylint: disable=unused-argument
                       no_wait=False):
    if is_azure_stack_profile(cmd) or vault_name:
        return sdk_no_wait(
            no_wait,
            client.begin_purge_deleted,
            location=location,
            vault_name=vault_name
        )
    return None