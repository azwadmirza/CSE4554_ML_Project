def arm_deploy_template_existing_storage(resource_group_name,
                                         registry_name,
                                         location,
                                         sku,
                                         storage_account_name,
                                         admin_user_enabled,
                                         deployment_name=None):
    """Deploys ARM template to create a container registry with an existing storage account.
    :param str resource_group_name: The name of resource group
    :param str registry_name: The name of container registry
    :param str location: The name of location
    :param str sku: The SKU of the container registry
    :param str storage_account_name: The name of storage account
    :param bool admin_user_enabled: Enable admin user
    :param str deployment_name: The name of the deployment
    """
    from azure.mgmt.resource.resources.models import DeploymentProperties
    from azure.cli.core.util import get_file_json
    import os

    storage_account_resource_group = \
        get_resource_group_name_by_storage_account_name(storage_account_name)

    parameters = _parameters(
        registry_name=registry_name,
        location=location,
        sku=sku,
        admin_user_enabled=admin_user_enabled,
        storage_account_name=storage_account_name,
        storage_account_resource_group=storage_account_resource_group)

    file_path = os.path.join(os.path.dirname(__file__), 'template_existing_storage.json')
    template = get_file_json(file_path)
    properties = DeploymentProperties(template=template, parameters=parameters, mode='incremental')

    return _arm_deploy_template(
        get_arm_service_client().deployments, resource_group_name, deployment_name, properties)