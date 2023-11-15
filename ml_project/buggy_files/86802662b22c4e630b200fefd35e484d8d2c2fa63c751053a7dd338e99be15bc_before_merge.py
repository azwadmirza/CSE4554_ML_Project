def create_vmss(cmd, vmss_name, resource_group_name, image,
                disable_overprovision=False, instance_count=2,
                location=None, tags=None, upgrade_policy_mode='manual', validate=False,
                admin_username=getpass.getuser(), admin_password=None, authentication_type=None,
                vm_sku=None, no_wait=False,
                ssh_dest_key_path=None, ssh_key_value=None, generate_ssh_keys=False,
                load_balancer=None, load_balancer_sku=None, application_gateway=None,
                app_gateway_subnet_address_prefix=None,
                app_gateway_sku='Standard_Large', app_gateway_capacity=10,
                backend_pool_name=None, nat_pool_name=None, backend_port=None, health_probe=None,
                public_ip_address=None, public_ip_address_allocation=None,
                public_ip_address_dns_name=None, accelerated_networking=None,
                public_ip_per_vm=False, vm_domain_name=None, dns_servers=None, nsg=None,
                os_caching=None, data_caching=None,
                storage_container_name='vhds', storage_sku=None,
                os_type=None, os_disk_name=None,
                use_unmanaged_disk=False, data_disk_sizes_gb=None, disk_info=None,
                vnet_name=None, vnet_address_prefix='10.0.0.0/16',
                subnet=None, subnet_address_prefix=None,
                os_offer=None, os_publisher=None, os_sku=None, os_version=None,
                load_balancer_type=None, app_gateway_type=None, vnet_type=None,
                public_ip_address_type=None, storage_profile=None,
                single_placement_group=None, custom_data=None, secrets=None, platform_fault_domain_count=None,
                plan_name=None, plan_product=None, plan_publisher=None, plan_promotion_code=None, license_type=None,
                assign_identity=None, identity_scope=None, identity_role='Contributor',
                identity_role_id=None, zones=None, priority=None, eviction_policy=None,
                application_security_groups=None):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from azure.cli.core.util import random_string, hash_string
    from azure.cli.core.commands.arm import ArmTemplateBuilder
    from azure.cli.command_modules.vm._template_builder import (StorageProfile, build_vmss_resource,
                                                                build_vnet_resource, build_public_ip_resource,
                                                                build_load_balancer_resource,
                                                                build_vmss_storage_account_pool_resource,
                                                                build_application_gateway_resource,
                                                                build_msi_role_assignment, build_nsg_resource)
    from msrestazure.tools import resource_id, is_valid_resource_id
    subscription_id = get_subscription_id(cmd.cli_ctx)
    network_id_template = resource_id(
        subscription=subscription_id, resource_group=resource_group_name,
        namespace='Microsoft.Network')

    vmss_id = resource_id(
        subscription=subscription_id, resource_group=resource_group_name,
        namespace='Microsoft.Compute', type='virtualMachineScaleSets', name=vmss_name)

    scrubbed_name = vmss_name.replace('-', '').lower()[:5]
    naming_prefix = '{}{}'.format(scrubbed_name,
                                  hash_string(vmss_id,
                                              length=(9 - len(scrubbed_name)),
                                              force_lower=True))

    # determine final defaults and calculated values
    tags = tags or {}
    os_disk_name = os_disk_name or ('osdisk_{}'.format(hash_string(vmss_id, length=10)) if use_unmanaged_disk else None)
    load_balancer = load_balancer or '{}LB'.format(vmss_name)
    app_gateway = application_gateway or '{}AG'.format(vmss_name)
    backend_pool_name = backend_pool_name or '{}BEPool'.format(load_balancer or application_gateway)

    # Build up the ARM template
    master_template = ArmTemplateBuilder()

    vmss_dependencies = []

    # VNET will always be a dependency
    if vnet_type == 'new':
        vnet_name = vnet_name or '{}VNET'.format(vmss_name)
        subnet = subnet or '{}Subnet'.format(vmss_name)
        vmss_dependencies.append('Microsoft.Network/virtualNetworks/{}'.format(vnet_name))
        vnet = build_vnet_resource(
            cmd, vnet_name, location, tags, vnet_address_prefix, subnet, subnet_address_prefix)
        if app_gateway_type:
            vnet['properties']['subnets'].append({
                'name': 'appGwSubnet',
                'properties': {
                    'addressPrefix': app_gateway_subnet_address_prefix
                }
            })
        master_template.add_resource(vnet)

    subnet_id = subnet if is_valid_resource_id(subnet) else \
        '{}/virtualNetworks/{}/subnets/{}'.format(network_id_template, vnet_name, subnet)
    gateway_subnet_id = ('{}/virtualNetworks/{}/subnets/appGwSubnet'.format(network_id_template, vnet_name)
                         if app_gateway_type == 'new' else None)

    # public IP is used by either load balancer/application gateway
    public_ip_address_id = None
    if public_ip_address:
        public_ip_address_id = (public_ip_address if is_valid_resource_id(public_ip_address)
                                else '{}/publicIPAddresses/{}'.format(network_id_template,
                                                                      public_ip_address))

    def _get_public_ip_address_allocation(value, sku):
        IPAllocationMethod = cmd.get_models('IPAllocationMethod', resource_type=ResourceType.MGMT_NETWORK)
        if not value:
            value = IPAllocationMethod.static.value if (sku and sku.lower() == 'standard') \
                else IPAllocationMethod.dynamic.value
        return value

    # Handle load balancer creation
    if load_balancer_type == 'new':
        vmss_dependencies.append('Microsoft.Network/loadBalancers/{}'.format(load_balancer))

        lb_dependencies = []
        if vnet_type == 'new':
            lb_dependencies.append('Microsoft.Network/virtualNetworks/{}'.format(vnet_name))
        if public_ip_address_type == 'new':
            public_ip_address = public_ip_address or '{}PublicIP'.format(load_balancer)
            lb_dependencies.append(
                'Microsoft.Network/publicIpAddresses/{}'.format(public_ip_address))
            master_template.add_resource(build_public_ip_resource(
                cmd, public_ip_address, location, tags,
                _get_public_ip_address_allocation(public_ip_address_allocation, load_balancer_sku),
                public_ip_address_dns_name, load_balancer_sku, zones))
            public_ip_address_id = '{}/publicIPAddresses/{}'.format(network_id_template,
                                                                    public_ip_address)

        # calculate default names if not provided
        nat_pool_name = nat_pool_name or '{}NatPool'.format(load_balancer)
        if not backend_port:
            backend_port = 3389 if os_type == 'windows' else 22

        lb_resource = build_load_balancer_resource(
            cmd, load_balancer, location, tags, backend_pool_name, nat_pool_name, backend_port,
            'loadBalancerFrontEnd', public_ip_address_id, subnet_id,
            private_ip_address='', private_ip_allocation='Dynamic', sku=load_balancer_sku)
        lb_resource['dependsOn'] = lb_dependencies
        master_template.add_resource(lb_resource)

        # Per https://docs.microsoft.com/en-us/azure/load-balancer/load-balancer-standard-overview#nsg
        if load_balancer_sku and load_balancer_sku.lower() == 'standard' and nsg is None:
            nsg_name = '{}NSG'.format(vmss_name)
            master_template.add_resource(build_nsg_resource(
                None, nsg_name, location, tags, 'rdp' if os_type.lower() == 'windows' else 'ssh'))
            nsg = "[resourceId('Microsoft.Network/networkSecurityGroups', '{}')]".format(nsg_name)
            vmss_dependencies.append('Microsoft.Network/networkSecurityGroups/{}'.format(nsg_name))

    # Or handle application gateway creation
    if app_gateway_type == 'new':
        vmss_dependencies.append('Microsoft.Network/applicationGateways/{}'.format(app_gateway))

        ag_dependencies = []
        if vnet_type == 'new':
            ag_dependencies.append('Microsoft.Network/virtualNetworks/{}'.format(vnet_name))
        if public_ip_address_type == 'new':
            public_ip_address = public_ip_address or '{}PublicIP'.format(app_gateway)
            ag_dependencies.append(
                'Microsoft.Network/publicIpAddresses/{}'.format(public_ip_address))
            master_template.add_resource(build_public_ip_resource(
                cmd, public_ip_address, location, tags,
                _get_public_ip_address_allocation(public_ip_address_allocation, None), public_ip_address_dns_name,
                None, zones))
            public_ip_address_id = '{}/publicIPAddresses/{}'.format(network_id_template,
                                                                    public_ip_address)

        # calculate default names if not provided
        backend_port = backend_port or 80

        ag_resource = build_application_gateway_resource(
            cmd, app_gateway, location, tags, backend_pool_name, backend_port, 'appGwFrontendIP',
            public_ip_address_id, subnet_id, gateway_subnet_id, private_ip_address='',
            private_ip_allocation='Dynamic', sku=app_gateway_sku, capacity=app_gateway_capacity)
        ag_resource['dependsOn'] = ag_dependencies
        master_template.add_variable(
            'appGwID',
            "[resourceId('Microsoft.Network/applicationGateways', '{}')]".format(app_gateway))
        master_template.add_resource(ag_resource)

    # create storage accounts if needed for unmanaged disk storage
    if storage_profile in [StorageProfile.SACustomImage, StorageProfile.SAPirImage]:
        master_template.add_resource(build_vmss_storage_account_pool_resource(
            cmd, 'storageLoop', location, tags, storage_sku))
        master_template.add_variable('storageAccountNames', [
            '{}{}'.format(naming_prefix, x) for x in range(5)
        ])
        master_template.add_variable('vhdContainers', [
            "[concat('https://', variables('storageAccountNames')[{}], '.blob.{}/{}')]".format(
                x, cmd.cli_ctx.cloud.suffixes.storage_endpoint, storage_container_name) for x in range(5)
        ])
        vmss_dependencies.append('storageLoop')

    backend_address_pool_id = None
    inbound_nat_pool_id = None
    if load_balancer_type or app_gateway_type:
        network_balancer = load_balancer if load_balancer_type else app_gateway
        balancer_type = 'loadBalancers' if load_balancer_type else 'applicationGateways'

        if is_valid_resource_id(network_balancer):
            # backend address pool needed by load balancer or app gateway
            backend_address_pool_id = '{}/backendAddressPools/{}'.format(network_balancer, backend_pool_name)
            if nat_pool_name:
                inbound_nat_pool_id = '{}/inboundNatPools/{}'.format(network_balancer, nat_pool_name)
        else:
            # backend address pool needed by load balancer or app gateway
            backend_address_pool_id = '{}/{}/{}/backendAddressPools/{}'.format(
                network_id_template, balancer_type, network_balancer, backend_pool_name)
            if nat_pool_name:
                inbound_nat_pool_id = '{}/{}/{}/inboundNatPools/{}'.format(
                    network_id_template, balancer_type, network_balancer, nat_pool_name)

        if health_probe and not is_valid_resource_id(health_probe):
            health_probe = '{}/loadBalancers/{}/probes/{}'.format(network_id_template, load_balancer, health_probe)

    ip_config_name = '{}IPConfig'.format(naming_prefix)
    nic_name = '{}Nic'.format(naming_prefix)

    if custom_data:
        custom_data = read_content_if_is_file(custom_data)

    if secrets:
        secrets = _merge_secrets([validate_file_or_dict(secret) for secret in secrets])

    vmss_resource = build_vmss_resource(
        cmd=cmd, name=vmss_name, naming_prefix=naming_prefix, location=location, tags=tags,
        overprovision=not disable_overprovision, upgrade_policy_mode=upgrade_policy_mode, vm_sku=vm_sku,
        instance_count=instance_count, ip_config_name=ip_config_name, nic_name=nic_name, subnet_id=subnet_id,
        public_ip_per_vm=public_ip_per_vm, vm_domain_name=vm_domain_name, dns_servers=dns_servers, nsg=nsg,
        accelerated_networking=accelerated_networking, admin_username=admin_username,
        authentication_type=authentication_type, storage_profile=storage_profile, os_disk_name=os_disk_name,
        disk_info=disk_info, storage_sku=storage_sku, os_type=os_type, image=image, admin_password=admin_password,
        ssh_key_value=ssh_key_value, ssh_key_path=ssh_dest_key_path, os_publisher=os_publisher, os_offer=os_offer,
        os_sku=os_sku, os_version=os_version, backend_address_pool_id=backend_address_pool_id,
        inbound_nat_pool_id=inbound_nat_pool_id, health_probe=health_probe,
        single_placement_group=single_placement_group, platform_fault_domain_count=platform_fault_domain_count,
        custom_data=custom_data, secrets=secrets, license_type=license_type, zones=zones, priority=priority,
        eviction_policy=eviction_policy, application_security_groups=application_security_groups)
    vmss_resource['dependsOn'] = vmss_dependencies

    if plan_name:
        vmss_resource['plan'] = {
            'name': plan_name,
            'publisher': plan_publisher,
            'product': plan_product,
            'promotionCode': plan_promotion_code
        }

    enable_local_identity = None
    if assign_identity is not None:
        vmss_resource['identity'], _, _, enable_local_identity = _build_identities_info(
            assign_identity)
        if identity_scope:
            role_assignment_guid = str(_gen_guid())
            master_template.add_resource(build_msi_role_assignment(vmss_name, vmss_id, identity_role_id,
                                                                   role_assignment_guid, identity_scope, False))

    master_template.add_resource(vmss_resource)
    master_template.add_output('VMSS', vmss_name, 'Microsoft.Compute', 'virtualMachineScaleSets',
                               output_type='object')

    if admin_password:
        master_template.add_secure_parameter('adminPassword', admin_password)

    template = master_template.build()
    parameters = master_template.build_parameters()

    # deploy ARM template
    deployment_name = 'vmss_deploy_' + random_string(32)
    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES).deployments
    DeploymentProperties = cmd.get_models('DeploymentProperties', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)

    properties = DeploymentProperties(template=template, parameters=parameters, mode='incremental')
    if validate:
        from azure.cli.command_modules.vm._vm_utils import log_pprint_template
        log_pprint_template(template)
        log_pprint_template(parameters)
        return sdk_no_wait(no_wait, client.validate, resource_group_name, deployment_name, properties)

    # creates the VMSS deployment
    deployment_result = DeploymentOutputLongRunningOperation(cmd.cli_ctx)(
        sdk_no_wait(no_wait, client.create_or_update, resource_group_name, deployment_name, properties))
    if assign_identity is not None:
        vmss_info = get_vmss(cmd, resource_group_name, vmss_name)
        if enable_local_identity and not identity_scope:
            _show_missing_access_warning(resource_group_name, vmss_name, 'vmss')
        deployment_result['vmss']['identity'] = _construct_identity_info(identity_scope, identity_role,
                                                                         vmss_info.identity.principal_id,
                                                                         vmss_info.identity.user_assigned_identities)
    return deployment_result