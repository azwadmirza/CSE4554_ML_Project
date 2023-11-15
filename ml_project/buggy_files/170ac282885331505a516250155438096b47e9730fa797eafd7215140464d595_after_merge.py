def acr_webhook_list_events(webhook_name,
                            registry_name,
                            resource_group_name=None):
    """Lists recent events for the specified webhook.
    :param str webhook_name: The name of webhook
    :param str registry_name: The name of container registry
    :param str resource_group_name: The name of resource group
    """
    _, resource_group_name = validate_managed_registry(
        registry_name, resource_group_name, WEBHOOKS_NOT_SUPPORTED)
    client = get_acr_service_client().webhooks

    return client.list_events(resource_group_name, registry_name, webhook_name)