def create_av_set(cmd, availability_set_name, resource_group_name,
                  platform_fault_domain_count=2, platform_update_domain_count=None,
                  location=None, no_wait=False,
                  unmanaged=False, tags=None, validate=False):
    from azure.cli.core.util import random_string
    from azure.cli.core.commands.arm import ArmTemplateBuilder
    from azure.cli.command_modules.vm._template_builder import build_av_set_resource

    tags = tags or {}

    # Build up the ARM template
    master_template = ArmTemplateBuilder()

    av_set_resource = build_av_set_resource(cmd, availability_set_name, location, tags,
                                            platform_update_domain_count,
                                            platform_fault_domain_count, unmanaged)
    master_template.add_resource(av_set_resource)

    template = master_template.build()

    # deploy ARM template
    deployment_name = 'av_set_deploy_' + random_string(32)
    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES).deployments
    DeploymentProperties = cmd.get_models('DeploymentProperties', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)

    properties = DeploymentProperties(template=template, parameters={}, mode='incremental')
    if validate:
        return client.validate(resource_group_name, deployment_name, properties)

    if no_wait:
        return client.create_or_update(
            resource_group_name, deployment_name, properties, raw=no_wait)

    LongRunningOperation(cmd.cli_ctx)(client.create_or_update(
        resource_group_name, deployment_name, properties, raw=no_wait))
    compute_client = _compute_client_factory(cmd.cli_ctx)
    return compute_client.availability_sets.get(resource_group_name, availability_set_name)