def acr_update_set(client,
                   registry_name,
                   resource_group_name=None,
                   parameters=None):
    """Sets the properties of the specified container registry.
    :param str registry_name: The name of container registry
    :param str resource_group_name: The name of resource group
    :param RegistryUpdateParameters parameters: The registry update parameters object
    """
    registry, resource_group_name = get_registry_by_name(registry_name, resource_group_name)

    validate_sku_update(registry.sku.name, parameters.sku)

    if registry.sku.name in MANAGED_REGISTRY_SKU and parameters.storage_account is not None:
        parameters.storage_account = None
        logger.warning(
            "The registry '%s' in '%s' SKU is a managed registry. The specified storage account will be ignored.",
            registry_name, registry.sku.name)

    return client.update(resource_group_name, registry_name, parameters)