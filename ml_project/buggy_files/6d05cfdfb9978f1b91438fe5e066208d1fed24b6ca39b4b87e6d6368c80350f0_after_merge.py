def get_resource_group_name_by_registry_name(registry_name,
                                             resource_group_name=None):
    """Returns the resource group name for the container registry.
    :param str registry_name: The name of container registry
    :param str resource_group_name: The name of resource group
    """
    if not resource_group_name:
        arm_resource = _arm_get_resource_by_name(registry_name, REGISTRY_RESOURCE_TYPE)
        resource_group_name = get_resource_group_name_by_resource_id(arm_resource.id)
    return resource_group_name