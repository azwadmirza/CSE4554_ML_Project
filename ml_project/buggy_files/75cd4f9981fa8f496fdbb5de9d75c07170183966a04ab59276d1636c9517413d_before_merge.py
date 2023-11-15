def build_vm_resource(  # pylint: disable=too-many-locals
        cmd, name, location, tags, size, storage_profile, nics, admin_username,
        availability_set_id=None, admin_password=None, ssh_key_value=None, ssh_key_path=None,
        image_reference=None, os_disk_name=None, custom_image_os_type=None,
        os_caching=None, data_caching=None, storage_sku=None,
        os_publisher=None, os_offer=None, os_sku=None, os_version=None, os_vhd_uri=None,
        attach_os_disk=None, os_disk_size_gb=None, attach_data_disks=None, data_disk_sizes_gb=None,
        image_data_disks=None, custom_data=None, secrets=None, license_type=None, zone=None):

    def _build_os_profile():

        os_profile = {
            'computerName': name,
            'adminUsername': admin_username
        }

        if admin_password:
            os_profile['adminPassword'] = admin_password

        if custom_data:
            os_profile['customData'] = b64encode(custom_data)

        if ssh_key_value and ssh_key_path:
            os_profile['linuxConfiguration'] = {
                'disablePasswordAuthentication': True,
                'ssh': {
                    'publicKeys': [
                        {
                            'keyData': ssh_key_value,
                            'path': ssh_key_path
                        }
                    ]
                }
            }

        if secrets:
            os_profile['secrets'] = secrets

        return os_profile

    def _build_storage_profile():

        storage_profiles = {
            'SACustomImage': {
                'osDisk': {
                    'createOption': 'fromImage',
                    'name': os_disk_name,
                    'caching': os_caching,
                    'osType': custom_image_os_type,
                    'image': {'uri': image_reference},
                    'vhd': {'uri': os_vhd_uri}
                }
            },
            'SAPirImage': {
                'osDisk': {
                    'createOption': 'fromImage',
                    'name': os_disk_name,
                    'caching': os_caching,
                    'vhd': {'uri': os_vhd_uri}
                },
                'imageReference': {
                    'publisher': os_publisher,
                    'offer': os_offer,
                    'sku': os_sku,
                    'version': os_version
                }
            },
            'SASpecializedOSDisk': {
                'osDisk': {
                    'createOption': 'attach',
                    'osType': custom_image_os_type,
                    'name': os_disk_name,
                    'vhd': {'uri': attach_os_disk}
                }
            },
            'ManagedPirImage': {
                'osDisk': {
                    'createOption': 'fromImage',
                    'name': os_disk_name,
                    'caching': os_caching,
                    'managedDisk': {'storageAccountType': storage_sku}
                },
                'imageReference': {
                    'publisher': os_publisher,
                    'offer': os_offer,
                    'sku': os_sku,
                    'version': os_version
                }
            },
            'ManagedCustomImage': {
                'osDisk': {
                    'createOption': 'fromImage',
                    'name': os_disk_name,
                    'caching': os_caching,
                    'managedDisk': {'storageAccountType': storage_sku}
                },
                "imageReference": {
                    'id': image_reference
                }
            },
            'ManagedSpecializedOSDisk': {
                'osDisk': {
                    'createOption': 'attach',
                    'osType': custom_image_os_type,
                    'managedDisk': {
                        'id': attach_os_disk
                    }
                }
            }
        }
        profile = storage_profiles[storage_profile.name]
        if os_disk_size_gb:
            profile['osDisk']['diskSizeGb'] = os_disk_size_gb
        return _build_data_disks(profile, data_disk_sizes_gb, image_data_disks,
                                 data_caching, storage_sku, attach_data_disks=attach_data_disks)

    vm_properties = {
        'hardwareProfile': {'vmSize': size},
        'networkProfile': {'networkInterfaces': nics}
    }

    vm_properties['storageProfile'] = _build_storage_profile()

    if availability_set_id:
        vm_properties['availabilitySet'] = {'id': availability_set_id}

    if not attach_os_disk:
        vm_properties['osProfile'] = _build_os_profile()

    if license_type:
        vm_properties['licenseType'] = license_type

    vm = {
        'apiVersion': cmd.get_api_version(ResourceType.MGMT_COMPUTE).virtual_machines,
        'type': 'Microsoft.Compute/virtualMachines',
        'name': name,
        'location': location,
        'tags': tags,
        'dependsOn': [],
        'properties': vm_properties,
    }
    if zone:
        vm['zones'] = zone
    return vm