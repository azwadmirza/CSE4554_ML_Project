def acr_webhook_get_config(webhook_name,
                           registry_name,
                           resource_group_name=None):
    """Gets the configuration of service URI and custom headers for the webhook.
    :param str webhook_name: The name of webhook
    :param str registry_name: The name of container registry
    :param str resource_group_name: The name of resource group
    """
    _, resource_group_name = managed_registry_validation(
        registry_name, resource_group_name, WEBHOOKS_NOT_SUPPORTED)
    client = get_acr_service_client(WEBHOOK_API_VERSION).webhooks

    return client.get_callback_config(resource_group_name, registry_name, webhook_name)