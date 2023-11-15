def create_vm(cmd, vm_name, resource_group_name, image=None, size='Standard_DS1_v2', location=None, tags=None,
              no_wait=False, authentication_type=None, admin_password=None,
              admin_username=getpass.getuser(), ssh_dest_key_path=None, ssh_key_value=None,
              generate_ssh_keys=False, availability_set=None, nics=None, nsg=None, nsg_rule=None,
              private_ip_address=None, public_ip_address=None, public_ip_address_allocation='dynamic',
              public_ip_address_dns_name=None, os_disk_name=None, os_type=None, storage_account=None,
              os_caching=None, data_caching=None, storage_container_name=None, storage_sku=None,
              use_unmanaged_disk=False, attach_os_disk=None, os_disk_size_gb=None,
              attach_data_disks=None, data_disk_sizes_gb=None, image_data_disks=None,
              vnet_name=None, vnet_address_prefix='10.0.0.0/16', subnet=None, subnet_address_prefix='10.0.0.0/24',
              storage_profile=None, os_publisher=None, os_offer=None, os_sku=None, os_version=None,
              storage_account_type=None, vnet_type=None, nsg_type=None, public_ip_type=None, nic_type=None,
              validate=False, custom_data=None, secrets=None, plan_name=None, plan_product=None, plan_publisher=None,
              plan_promotion_code=None, license_type=None, assign_identity=None, identity_scope=None,
              identity_role='Contributor', identity_role_id=None, application_security_groups=None,
              zone=None):
    from azure.cli.core.commands.client_factory import get_subscription_id
    from azure.cli.core.util import random_string, hash_string
    from azure.cli.core.commands.arm import ArmTemplateBuilder
    from azure.cli.command_modules.vm._template_builder import (build_vm_resource,
                                                                build_storage_account_resource, build_nic_resource,
                                                                build_vnet_resource, build_nsg_resource,
                                                                build_public_ip_resource, StorageProfile,
                                                                build_msi_role_assignment, build_vm_msi_extension)

    subscription_id = get_subscription_id(cmd.cli_ctx)
    network_id_template = resource_id(
        subscription=subscription_id, resource_group=resource_group_name,
        namespace='Microsoft.Network')

    vm_id = resource_id(
        subscription=subscription_id, resource_group=resource_group_name,
        namespace='Microsoft.Compute', type='virtualMachines', name=vm_name)

    # determine final defaults and calculated values
    tags = tags or {}
    os_disk_name = os_disk_name or ('osdisk_{}'.format(hash_string(vm_id, length=10)) if use_unmanaged_disk else None)
    storage_container_name = storage_container_name or 'vhds'

    # Build up the ARM template
    master_template = ArmTemplateBuilder()

    vm_dependencies = []
    if storage_account_type == 'new':
        storage_account = storage_account or 'vhdstorage{}'.format(
            hash_string(vm_id, length=14, force_lower=True))
        vm_dependencies.append('Microsoft.Storage/storageAccounts/{}'.format(storage_account))
        master_template.add_resource(build_storage_account_resource(cmd, storage_account, location,
                                                                    tags, storage_sku))

    nic_name = None
    if nic_type == 'new':
        nic_name = '{}VMNic'.format(vm_name)
        vm_dependencies.append('Microsoft.Network/networkInterfaces/{}'.format(nic_name))

        nic_dependencies = []
        if vnet_type == 'new':
            vnet_name = vnet_name or '{}VNET'.format(vm_name)
            subnet = subnet or '{}Subnet'.format(vm_name)
            nic_dependencies.append('Microsoft.Network/virtualNetworks/{}'.format(vnet_name))
            master_template.add_resource(build_vnet_resource(
                cmd, vnet_name, location, tags, vnet_address_prefix, subnet, subnet_address_prefix))

        if nsg_type == 'new':
            nsg_rule_type = 'rdp' if os_type.lower() == 'windows' else 'ssh'
            nsg = nsg or '{}NSG'.format(vm_name)
            nic_dependencies.append('Microsoft.Network/networkSecurityGroups/{}'.format(nsg))
            master_template.add_resource(build_nsg_resource(cmd, nsg, location, tags, nsg_rule_type))

        if public_ip_type == 'new':
            public_ip_address = public_ip_address or '{}PublicIP'.format(vm_name)
            nic_dependencies.append('Microsoft.Network/publicIpAddresses/{}'.format(
                public_ip_address))
            master_template.add_resource(build_public_ip_resource(cmd, public_ip_address, location, tags,
                                                                  public_ip_address_allocation,
                                                                  public_ip_address_dns_name,
                                                                  None, zone))

        subnet_id = subnet if is_valid_resource_id(subnet) else \
            '{}/virtualNetworks/{}/subnets/{}'.format(network_id_template, vnet_name, subnet)

        nsg_id = None
        if nsg:
            nsg_id = nsg if is_valid_resource_id(nsg) else \
                '{}/networkSecurityGroups/{}'.format(network_id_template, nsg)

        public_ip_address_id = None
        if public_ip_address:
            public_ip_address_id = public_ip_address if is_valid_resource_id(public_ip_address) \
                else '{}/publicIPAddresses/{}'.format(network_id_template, public_ip_address)

        nics = [
            {'id': '{}/networkInterfaces/{}'.format(network_id_template, nic_name)}
        ]
        nic_resource = build_nic_resource(
            cmd, nic_name, location, tags, vm_name, subnet_id, private_ip_address, nsg_id,
            public_ip_address_id, application_security_groups)
        nic_resource['dependsOn'] = nic_dependencies
        master_template.add_resource(nic_resource)
    else:
        # Using an existing NIC
        invalid_parameters = [nsg, public_ip_address, subnet, vnet_name, application_security_groups]
        if any(invalid_parameters):
            raise CLIError('When specifying an existing NIC, do not specify NSG, '
                           'public IP, ASGs, VNet or subnet.')

    os_vhd_uri = None
    if storage_profile in [StorageProfile.SACustomImage, StorageProfile.SAPirImage]:
        storage_account_name = storage_account.rsplit('/', 1)
        storage_account_name = storage_account_name[1] if \
            len(storage_account_name) > 1 else storage_account_name[0]
        os_vhd_uri = 'https://{}.blob.{}/{}/{}.vhd'.format(
            storage_account_name, cmd.cli_ctx.cloud.suffixes.storage_endpoint, storage_container_name, os_disk_name)
    elif storage_profile == StorageProfile.SASpecializedOSDisk:
        os_vhd_uri = attach_os_disk
        os_disk_name = attach_os_disk.rsplit('/', 1)[1][:-4]

    if custom_data:
        custom_data = read_content_if_is_file(custom_data)

    if secrets:
        secrets = _merge_secrets([validate_file_or_dict(secret) for secret in secrets])

    vm_resource = build_vm_resource(
        cmd, vm_name, location, tags, size, storage_profile, nics, admin_username, availability_set,
        admin_password, ssh_key_value, ssh_dest_key_path, image, os_disk_name,
        os_type, os_caching, data_caching, storage_sku, os_publisher, os_offer, os_sku, os_version,
        os_vhd_uri, attach_os_disk, os_disk_size_gb, attach_data_disks, data_disk_sizes_gb, image_data_disks,
        custom_data, secrets, license_type, zone)
    vm_resource['dependsOn'] = vm_dependencies

    if plan_name:
        vm_resource['plan'] = {
            'name': plan_name,
            'publisher': plan_publisher,
            'product': plan_product,
            'promotionCode': plan_promotion_code
        }

    enable_local_identity, external_identities = None, None
    if assign_identity is not None:
        vm_resource['identity'], _, external_identities, enable_local_identity = _build_identities_info(assign_identity)
        role_assignment_guid = None
        if identity_scope:
            role_assignment_guid = str(_gen_guid())
            master_template.add_resource(build_msi_role_assignment(cmd, vm_name, vm_id, identity_role_id,
                                                                   role_assignment_guid, identity_scope))
        master_template.add_resource(build_vm_msi_extension(cmd, vm_name, location, role_assignment_guid, _MSI_PORT,
                                                            os_type.lower() != 'windows', _MSI_EXTENSION_VERSION))

    master_template.add_resource(vm_resource)

    if admin_password:
        master_template.add_secure_parameter('adminPassword', admin_password)

    template = master_template.build()
    parameters = master_template.build_parameters()

    # deploy ARM template
    deployment_name = 'vm_deploy_' + random_string(32)
    client = get_mgmt_service_client(cmd.cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES).deployments
    DeploymentProperties = cmd.get_models('DeploymentProperties', resource_type=ResourceType.MGMT_RESOURCE_RESOURCES)
    properties = DeploymentProperties(template=template, parameters=parameters, mode='incremental')
    if validate:
        from azure.cli.command_modules.vm._vm_utils import log_pprint_template
        log_pprint_template(template)
        log_pprint_template(parameters)
        return client.validate(resource_group_name, deployment_name, properties)

    # creates the VM deployment
    if no_wait:
        return client.create_or_update(
            resource_group_name, deployment_name, properties, raw=no_wait)
    else:
        LongRunningOperation(cmd.cli_ctx)(client.create_or_update(
            resource_group_name, deployment_name, properties, raw=no_wait))
    vm = get_vm_details(cmd, resource_group_name, vm_name)
    if assign_identity is not None:
        if enable_local_identity and not identity_scope:
            _show_missing_access_warning(resource_group_name, vm_name, 'vm')
        setattr(vm, 'identity', _construct_identity_info(identity_scope, identity_role, _MSI_PORT, external_identities))
    return vm