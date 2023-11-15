def acr_show_usage(registry_name, resource_group_name=None):
    """Gets the quota usages for the specified container registry.
    :param str registry_name: The name of container registry
    :param str resource_group_name: The name of resource group
    """
    _, resource_group_name = managed_registry_validation(
        registry_name, resource_group_name, "Usage is not supported for registries in Basic SKU.")
    client = get_acr_service_client(MANAGED_REGISTRY_API_VERSION).registries

    return client.list_usages(resource_group_name, registry_name)