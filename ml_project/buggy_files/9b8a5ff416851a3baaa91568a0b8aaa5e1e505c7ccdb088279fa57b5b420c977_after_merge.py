def _parameters(registry_name,
                location,
                sku,
                admin_user_enabled,
                storage_account_name=None,
                storage_account_id=None,
                registry_api_version=None):
    """Returns a dict of deployment parameters.
    :param str registry_name: The name of container registry
    :param str location: The name of location
    :param str sku: The SKU of the container registry
    :param bool admin_user_enabled: Enable admin user
    :param str storage_account_name: The name of storage account
    :param str storage_account_id: The resource ID of storage account
    :param str registry_api_version: The API version of the container registry
    """
    parameters = {
        'registryName': {'value': registry_name},
        'registryLocation': {'value': location},
        'registrySku': {'value': sku},
        'adminUserEnabled': {'value': admin_user_enabled}
    }
    if registry_api_version:
        parameters['registryApiVersion'] = {'value': registry_api_version}
    if storage_account_name:
        parameters['storageAccountName'] = {'value': storage_account_name}
    if storage_account_id:
        parameters['storageAccountId'] = {'value': storage_account_id}

    return parameters