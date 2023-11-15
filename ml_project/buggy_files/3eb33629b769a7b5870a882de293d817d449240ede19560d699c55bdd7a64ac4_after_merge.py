def validate_deleted_vault_or_hsm_name(cmd, ns):
    """
    Validate a deleted vault name; populate or validate location and resource_group_name
    """
    from azure.cli.core.profiles import ResourceType
    from msrestazure.tools import parse_resource_id

    vault_name = getattr(ns, 'vault_name', None)
    hsm_name = getattr(ns, 'hsm_name', None)

    if hsm_name:
        raise InvalidArgumentValueError('Operation "purge" has not been supported for HSM.')

    if not vault_name and not hsm_name:
        raise CLIError('Please specify --vault-name or --hsm-name.')

    if vault_name:
        resource_name = vault_name
    else:
        resource_name = hsm_name
    resource = None

    if vault_name:
        client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_KEYVAULT).vaults
    else:
        client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_KEYVAULT).managed_hsms

    # if the location is specified, use get_deleted rather than list_deleted
    if ns.location:
        resource = client.get_deleted(resource_name, ns.location)
        if vault_name:
            id_comps = parse_resource_id(resource.properties.vault_id)
        else:
            id_comps = parse_resource_id(resource.properties.id)

    # otherwise, iterate through deleted vaults to find one with a matching name
    else:
        for v in client.list_deleted():
            if vault_name:
                id_comps = parse_resource_id(v.properties.vault_id)
            else:
                id_comps = parse_resource_id(v.properties.id)
            if id_comps['name'].lower() == resource_name.lower():
                resource = v
                ns.location = resource.properties.location
                break

    # if the vault was not found, throw an error
    if not resource:
        raise CLIError('No deleted Vault or HSM was found with name ' + resource_name)

    if 'keyvault purge' not in cmd.name:
        setattr(ns, 'resource_group_name', getattr(ns, 'resource_group_name', None) or id_comps['resource_group'])

        # resource_group_name must match the resource group of the deleted vault
        if id_comps['resource_group'] != ns.resource_group_name:
            raise CLIError("The specified resource group does not match that of the deleted vault or hsm %s. The vault "
                           "or hsm must be recovered to the original resource group %s."
                           % (vault_name, id_comps['resource_group']))