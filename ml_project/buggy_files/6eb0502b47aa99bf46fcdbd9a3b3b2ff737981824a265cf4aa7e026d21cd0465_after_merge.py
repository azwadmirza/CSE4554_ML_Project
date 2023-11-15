def get_vm_format_secret(cmd, secrets, certificate_store=None, keyvault=None, resource_group_name=None):
    from azure.mgmt.keyvault import KeyVaultManagementClient
    from azure.keyvault import KeyVaultId
    import re
    client = get_mgmt_service_client(cmd.cli_ctx, KeyVaultManagementClient).vaults
    grouped_secrets = {}

    merged_secrets = []
    for s in secrets:
        merged_secrets += s.splitlines()

    # group secrets by source vault
    for secret in merged_secrets:
        parsed = KeyVaultId.parse_secret_id(secret)
        match = re.search('://(.+?)\\.', parsed.vault)
        vault_name = match.group(1)
        if vault_name not in grouped_secrets:
            grouped_secrets[vault_name] = {
                'vaultCertificates': [],
                'id': keyvault or _get_vault_id_from_name(cmd.cli_ctx, client, vault_name)
            }

        vault_cert = {'certificateUrl': secret}
        if certificate_store:
            vault_cert['certificateStore'] = certificate_store

        grouped_secrets[vault_name]['vaultCertificates'].append(vault_cert)

    # transform the reduced map to vm format
    formatted = [{'sourceVault': {'id': value['id']},
                  'vaultCertificates': value['vaultCertificates']}
                 for _, value in list(grouped_secrets.items())]

    return formatted