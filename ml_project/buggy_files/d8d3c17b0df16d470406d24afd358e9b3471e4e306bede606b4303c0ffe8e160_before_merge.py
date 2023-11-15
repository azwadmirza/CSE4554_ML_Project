def acr_update_get(client,  # pylint: disable=unused-argument
                   registry_name,
                   resource_group_name=None):
    """Returns an empty RegistryUpdateParameters object.
    :param str registry_name: The name of container registry
    :param str resource_group_name: The name of resource group
    """
    try:
        managed_registry_validation(registry_name, resource_group_name)
        return ManagedRegistryUpdateParameters()
    except:  # pylint: disable=bare-except
        return BasicRegistryUpdateParameters()