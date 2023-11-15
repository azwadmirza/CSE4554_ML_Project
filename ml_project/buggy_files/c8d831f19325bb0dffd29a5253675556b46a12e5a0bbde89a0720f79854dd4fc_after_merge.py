def build_vmss_resource(cmd, name, naming_prefix, location, tags, overprovision, upgrade_policy_mode,
                        vm_sku, instance_count, ip_config_name, nic_name, subnet_id,
                        public_ip_per_vm, vm_domain_name, dns_servers, nsg, accelerated_networking,
                        admin_username, authentication_type, storage_profile, os_disk_name,
                        os_caching, data_caching, storage_sku, data_disk_sizes_gb, image_data_disks, os_type,
                        image=None, admin_password=None, ssh_key_value=None, ssh_key_path=None,
                        os_publisher=None, os_offer=None, os_sku=None, os_version=None,
                        backend_address_pool_id=None, inbound_nat_pool_id=None, health_probe=None,
                        single_placement_group=None, custom_data=None, secrets=None, license_type=None,
                        zones=None, priority=None):

    # Build IP configuration
    ip_configuration = {
        'name': ip_config_name,
        'properties': {
            'subnet': {'id': subnet_id}
        }
    }

    if public_ip_per_vm:
        ip_configuration['properties']['publicipaddressconfiguration'] = {
            'name': 'instancepublicip',
            'properties': {
                'idleTimeoutInMinutes': 10,
            }
        }
        if vm_domain_name:
            ip_configuration['properties']['publicipaddressconfiguration']['properties']['dnsSettings'] = {
                'domainNameLabel': vm_domain_name
            }

    if backend_address_pool_id:
        key = 'loadBalancerBackendAddressPools' if 'loadBalancers' in backend_address_pool_id \
            else 'ApplicationGatewayBackendAddressPools'
        ip_configuration['properties'][key] = [
            {'id': backend_address_pool_id}
        ]

    if inbound_nat_pool_id:
        ip_configuration['properties']['loadBalancerInboundNatPools'] = [
            {'id': inbound_nat_pool_id}
        ]

    # Build storage profile
    storage_properties = {}
    if storage_profile in [StorageProfile.SACustomImage, StorageProfile.SAPirImage]:
        storage_properties['osDisk'] = {
            'name': os_disk_name,
            'caching': os_caching,
            'createOption': 'FromImage',
        }

        if storage_profile == StorageProfile.SACustomImage:
            storage_properties['osDisk'].update({
                'osType': os_type,
                'image': {
                    'uri': image
                }
            })
        else:
            storage_properties['osDisk']['vhdContainers'] = "[variables('vhdContainers')]"
    elif storage_profile in [StorageProfile.ManagedPirImage, StorageProfile.ManagedCustomImage]:
        storage_properties['osDisk'] = {
            'createOption': 'FromImage',
            'caching': os_caching,
            'managedDisk': {'storageAccountType': storage_sku}
        }

    if storage_profile in [StorageProfile.SAPirImage, StorageProfile.ManagedPirImage]:
        storage_properties['imageReference'] = {
            'publisher': os_publisher,
            'offer': os_offer,
            'sku': os_sku,
            'version': os_version
        }
    if storage_profile == StorageProfile.ManagedCustomImage:
        storage_properties['imageReference'] = {
            'id': image
        }

    storage_profile = _build_data_disks(storage_properties, data_disk_sizes_gb,
                                        image_data_disks, data_caching,
                                        storage_sku)

    # Build OS Profile
    os_profile = {
        'computerNamePrefix': naming_prefix,
        'adminUsername': admin_username
    }
    if authentication_type == 'password' and admin_password:
        os_profile['adminPassword'] = "[parameters('adminPassword')]"
    else:
        os_profile['linuxConfiguration'] = {
            'disablePasswordAuthentication': True,
            'ssh': {
                'publicKeys': [
                    {
                        'path': ssh_key_path,
                        'keyData': ssh_key_value
                    }
                ]
            }
        }

    if custom_data:
        os_profile['customData'] = b64encode(custom_data)

    if secrets:
        os_profile['secrets'] = secrets

    if single_placement_group is None:  # this should never happen, but just in case
        raise ValueError('single_placement_group was not set by validators')
    # Build VMSS
    nic_config = {
        'name': nic_name,
        'properties': {
            'primary': 'true',
            'ipConfigurations': [ip_configuration]
        }
    }

    if cmd.supported_api_version(min_api='2017-03-30').virtual_machine_scale_sets:  # pylint: disable=no-member
        if dns_servers:
            nic_config['properties']['dnsSettings'] = {'dnsServers': dns_servers}

        if accelerated_networking:
            nic_config['properties']['enableAcceleratedNetworking'] = True

    if nsg:
        nic_config['properties']['networkSecurityGroup'] = {'id': nsg}

    vmss_properties = {
        'overprovision': overprovision,
        'upgradePolicy': {
            'mode': upgrade_policy_mode
        },
        'virtualMachineProfile': {
            'storageProfile': storage_properties,
            'osProfile': os_profile,
            'networkProfile': {
                'networkInterfaceConfigurations': [nic_config]
            }
        }
    }

    if license_type:
        vmss_properties['virtualMachineProfile']['licenseType'] = license_type

    if health_probe and cmd.supported_api_version(min_api='2017-03-30').virtual_machine_scale_sets:  # pylint: disable=no-member
        vmss_properties['virtualMachineProfile']['networkProfile']['healthProbe'] = {'id': health_probe}

    if cmd.supported_api_version(min_api='2016-04-30-preview').virtual_machine_scale_sets:  # pylint: disable=no-member
        vmss_properties['singlePlacementGroup'] = single_placement_group

    if priority and cmd.supported_api_version(min_api='2017-12-01').virtual_machine_scale_sets:  # pylint: disable=no-member
        vmss_properties['virtualMachineProfile']['priority'] = priority

    vmss = {
        'type': 'Microsoft.Compute/virtualMachineScaleSets',
        'name': name,
        'location': location,
        'tags': tags,
        'apiVersion': cmd.get_api_version(ResourceType.MGMT_COMPUTE).virtual_machine_scale_sets,  # pylint: disable=no-member
        'dependsOn': [],
        'sku': {
            'name': vm_sku,
            'capacity': instance_count
        },
        'properties': vmss_properties
    }
    if zones:
        vmss['zones'] = zones
    return vmss