def acr_webhook_create(webhook_name,
                       uri,
                       actions,
                       registry_name,
                       resource_group_name=None,
                       headers=None,
                       status='enabled',
                       scope=None,
                       tags=None):
    """Creates a webhook for a container registry.
    :param str webhook_name: The name of webhook
    :param str uri: The service URI for the webhook to post notifications
    :param str actions: The list of actions that trigger the webhook to post notifications
    :param str registry_name: The name of container registry
    :param str resource_group_name: The name of resource group
    :param str headers: Custom headers that will be added to the webhook notifications
    :param str status: Indicates whether the webhook is enabled
    :param str scope: The scope of repositories where the event can be triggered
    """
    registry, resource_group_name = validate_managed_registry(
        registry_name, resource_group_name, WEBHOOKS_NOT_SUPPORTED)

    client = get_acr_service_client().webhooks

    return client.create(
        resource_group_name,
        registry_name,
        webhook_name,
        WebhookCreateParameters(
            location=registry.location,
            service_uri=uri,
            actions=actions,
            custom_headers=headers,
            status=status,
            scope=scope,
            tags=tags
        )
    )