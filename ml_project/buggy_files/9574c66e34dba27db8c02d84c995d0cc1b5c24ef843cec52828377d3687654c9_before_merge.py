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

    if registry.sku.tier == SkuTier.managed.value:
        if parameters.sku is not None:
            validate_sku_update(parameters.sku)
        if parameters.storage_account is not None:
            parameters.storage_account = None
            logger.warning(
                "The registry '%s' in '%s' SKU is a managed registry. The specified storage account will be ignored.",
                registry_name, registry.sku.name)
        client = get_acr_service_client(MANAGED_REGISTRY_API_VERSION).registries
    elif registry.sku.tier == SkuTier.basic.value:
        if hasattr(parameters, 'sku') and parameters.sku is not None:
            parameters.sku = None
            logger.warning(
                "Updating SKU is not supported for registries in Basic SKU. The specified SKU will be ignored.")
        if parameters.storage_account is not None:
            parameters.storage_account = ensure_storage_account_parameter(parameters.storage_account)

    return client.update(resource_group_name, registry_name, parameters)