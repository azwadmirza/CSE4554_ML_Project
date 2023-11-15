def _manage_devices(devices, vm=None, container_ref=None, new_vm_name=None):
    unit_number = 0
    bus_number = 0
    device_specs = []
    existing_disks_label = []
    existing_scsi_controllers_label = []
    existing_ide_controllers_label = []
    existing_network_adapters_label = []
    existing_cd_drives_label = []
    ide_controllers = {}
    nics_map = []
    cloning_from_vm = vm is not None

    if cloning_from_vm:
        # loop through all the devices the vm/template has
        # check if the device needs to be created or configured
        for device in vm.config.hardware.device:
            if isinstance(device, vim.vm.device.VirtualDisk):
                # this is a hard disk
                if 'disk' in list(devices.keys()):
                    # there is atleast one disk specified to be created/configured
                    unit_number += 1
                    existing_disks_label.append(device.deviceInfo.label)
                    if device.deviceInfo.label in list(devices['disk'].keys()):
                        disk_spec = None
                        if 'size' in devices['disk'][device.deviceInfo.label]:
                            size_gb = float(devices['disk'][device.deviceInfo.label]['size'])
                            size_kb = int(size_gb * 1024.0 * 1024.0)
                        else:
                            # User didn't specify disk size in the cloud
                            # profile so use the existing disk size
                            size_kb = device.capacityInKB
                            size_gb = size_kb / (1024.0 * 1024.0)
                            log.debug(
                                'Virtual disk size for \'{0}\' was not '
                                'specified in the cloud profile or map file. '
                                'Using existing virtual disk size of \'{1}GB\''.format(
                                    device.deviceInfo.label,
                                    size_gb
                                )
                            )

                        if device.capacityInKB > size_kb:
                            raise SaltCloudSystemExit(
                                'The specified disk size \'{0}GB\' for \'{1}\' is '
                                'smaller than the disk image size \'{2}GB\'. It must '
                                'be equal to or greater than the disk image'.format(
                                    float(devices['disk'][device.deviceInfo.label]['size']),
                                    device.deviceInfo.label,
                                    float(device.capacityInKB / (1024.0 * 1024.0))
                                )
                            )
                        else:
                            disk_spec = _get_size_spec(device=device, size_kb=size_kb)

                        if 'mode' in devices['disk'][device.deviceInfo.label]:
                            if devices['disk'][device.deviceInfo.label]['mode'] \
                                in [
                                    'independent_persistent',
                                    'independent_nonpersistent',
                                    'dependent',
                            ]:
                                mode = devices['disk'][device.deviceInfo.label]['mode']
                                disk_spec = _get_mode_spec(device, mode, disk_spec)
                            else:
                                raise SaltCloudSystemExit('Invalid disk'
                                                          ' backing mode'
                                                          ' specified!')
                        if disk_spec is not None:
                            device_specs.append(disk_spec)

            elif isinstance(device.backing, vim.vm.device.VirtualEthernetCard.NetworkBackingInfo) or isinstance(device.backing, vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo):
                # this is a network adapter
                if 'network' in list(devices.keys()):
                    # there is atleast one network adapter specified to be created/configured
                    existing_network_adapters_label.append(device.deviceInfo.label)
                    if device.deviceInfo.label in list(devices['network'].keys()):
                        network_name = devices['network'][device.deviceInfo.label]['name']
                        adapter_type = devices['network'][device.deviceInfo.label]['adapter_type'] if 'adapter_type' in devices['network'][device.deviceInfo.label] else ''
                        switch_type = devices['network'][device.deviceInfo.label]['switch_type'] if 'switch_type' in devices['network'][device.deviceInfo.label] else ''
                        network_spec = _edit_existing_network_adapter(device, network_name, adapter_type, switch_type)
                        adapter_mapping = _set_network_adapter_mapping(devices['network'][device.deviceInfo.label])
                        device_specs.append(network_spec)
                        nics_map.append(adapter_mapping)

            elif hasattr(device, 'scsiCtlrUnitNumber'):
                # this is a SCSI controller
                if 'scsi' in list(devices.keys()):
                    # there is atleast one SCSI controller specified to be created/configured
                    bus_number += 1
                    existing_scsi_controllers_label.append(device.deviceInfo.label)
                    if device.deviceInfo.label in list(devices['scsi'].keys()):
                        # Modify the existing SCSI controller
                        scsi_controller_properties = devices['scsi'][device.deviceInfo.label]
                        bus_sharing = scsi_controller_properties['bus_sharing'].strip().lower() if 'bus_sharing' in scsi_controller_properties else None
                        if bus_sharing and bus_sharing in ['virtual', 'physical', 'no']:
                            bus_sharing = '{0}Sharing'.format(bus_sharing)
                            if bus_sharing != device.sharedBus:
                                # Only edit the SCSI controller if bus_sharing is different
                                scsi_spec = _edit_existing_scsi_controller(device, bus_sharing)
                                device_specs.append(scsi_spec)

            elif isinstance(device, vim.vm.device.VirtualCdrom):
                # this is a cd/dvd drive
                if 'cd' in list(devices.keys()):
                    # there is atleast one cd/dvd drive specified to be created/configured
                    existing_cd_drives_label.append(device.deviceInfo.label)
                    if device.deviceInfo.label in list(devices['cd'].keys()):
                        device_type = devices['cd'][device.deviceInfo.label]['device_type'] if 'device_type' in devices['cd'][device.deviceInfo.label] else ''
                        mode = devices['cd'][device.deviceInfo.label]['mode'] if 'mode' in devices['cd'][device.deviceInfo.label] else ''
                        iso_path = devices['cd'][device.deviceInfo.label]['iso_path'] if 'iso_path' in devices['cd'][device.deviceInfo.label] else ''
                        cd_drive_spec = _edit_existing_cd_or_dvd_drive(device, device_type, mode, iso_path)
                        device_specs.append(cd_drive_spec)

            elif isinstance(device, vim.vm.device.VirtualIDEController):
                # this is an IDE controller to add new cd drives to
                ide_controllers[device.key] = len(device.device)

    if 'network' in list(devices.keys()):
        network_adapters_to_create = list(set(devices['network'].keys()) - set(existing_network_adapters_label))
        network_adapters_to_create.sort()
        log.debug("Networks adapters to create: {0}".format(network_adapters_to_create)) if network_adapters_to_create else None  # pylint: disable=W0106
        for network_adapter_label in network_adapters_to_create:
            network_name = devices['network'][network_adapter_label]['name']
            adapter_type = devices['network'][network_adapter_label]['adapter_type'] if 'adapter_type' in devices['network'][network_adapter_label] else ''
            switch_type = devices['network'][network_adapter_label]['switch_type'] if 'switch_type' in devices['network'][network_adapter_label] else ''
            mac = devices['network'][network_adapter_label]['mac'] if 'mac' in devices['network'][network_adapter_label] else ''
            # create the network adapter
            network_spec = _add_new_network_adapter_helper(network_adapter_label, network_name, adapter_type, switch_type, mac, container_ref)
            adapter_mapping = _set_network_adapter_mapping(devices['network'][network_adapter_label])
            device_specs.append(network_spec)
            nics_map.append(adapter_mapping)

    if 'scsi' in list(devices.keys()):
        scsi_controllers_to_create = list(set(devices['scsi'].keys()) - set(existing_scsi_controllers_label))
        scsi_controllers_to_create.sort()
        log.debug("SCSI controllers to create: {0}".format(scsi_controllers_to_create)) if scsi_controllers_to_create else None  # pylint: disable=W0106
        for scsi_controller_label in scsi_controllers_to_create:
            # create the SCSI controller
            scsi_controller_properties = devices['scsi'][scsi_controller_label]
            scsi_spec = _add_new_scsi_controller_helper(scsi_controller_label, scsi_controller_properties, bus_number)
            device_specs.append(scsi_spec)
            bus_number += 1

    if 'ide' in list(devices.keys()):
        ide_controllers_to_create = list(set(devices['ide'].keys()) - set(existing_ide_controllers_label))
        ide_controllers_to_create.sort()
        log.debug('IDE controllers to create: {0}'.format(ide_controllers_to_create)) if ide_controllers_to_create else None  # pylint: disable=W0106

        # ESX 5.5 (and possibly earlier?) set the IDE controller key themselves, indexed starting at
        # 200. Rather than doing a create task/get vm/reconfig task dance we query the server and
        # if it's ESX 5.5 we supply a controller starting at 200 and work out way upwards from there
        # ESX 6 (and, one assumes, vCenter) does not display this problem and so continues to use
        # the randomly generated indexes
        vcenter_name = get_vcenter_version(call='function')
        controller_index = SAFE_ESX_5_5_CONTROLLER_KEY_INDEX if ESX_5_5_NAME_PORTION in vcenter_name else None

        for ide_controller_label in ide_controllers_to_create:
            # create the IDE controller
            ide_spec = _add_new_ide_controller_helper(ide_controller_label, controller_index, bus_number)
            device_specs.append(ide_spec)
            bus_number += 1
            if controller_index is not None:
                controller_index += 1

    if 'disk' in list(devices.keys()):
        disks_to_create = list(set(devices['disk'].keys()) - set(existing_disks_label))
        disks_to_create.sort()
        log.debug("Hard disks to create: {0}".format(disks_to_create)) if disks_to_create else None  # pylint: disable=W0106
        for disk_label in disks_to_create:
            # create the disk
            size_gb = float(devices['disk'][disk_label]['size'])
            thin_provision = bool(devices['disk'][disk_label]['thin_provision']) if 'thin_provision' in devices['disk'][disk_label] else False
            datastore = devices['disk'][disk_label].get('datastore', None)
            disk_spec = _add_new_hard_disk_helper(disk_label, size_gb, unit_number, thin_provision=thin_provision, datastore=datastore, vm_name=new_vm_name)

            # when creating both SCSI controller and Hard disk at the same time we need the randomly
            # assigned (temporary) key of the newly created SCSI controller
            if 'controller' in devices['disk'][disk_label]:
                for spec in device_specs:
                    if spec.device.deviceInfo.label == devices['disk'][disk_label]['controller']:
                        disk_spec.device.controllerKey = spec.device.key
                        break

            device_specs.append(disk_spec)
            unit_number += 1

    if 'cd' in list(devices.keys()):
        cd_drives_to_create = list(set(devices['cd'].keys()) - set(existing_cd_drives_label))
        cd_drives_to_create.sort()
        log.debug("CD/DVD drives to create: {0}".format(cd_drives_to_create)) if cd_drives_to_create else None  # pylint: disable=W0106
        for cd_drive_label in cd_drives_to_create:
            # create the CD/DVD drive
            device_type = devices['cd'][cd_drive_label]['device_type'] if 'device_type' in devices['cd'][cd_drive_label] else ''
            mode = devices['cd'][cd_drive_label]['mode'] if 'mode' in devices['cd'][cd_drive_label] else ''
            iso_path = devices['cd'][cd_drive_label]['iso_path'] if 'iso_path' in devices['cd'][cd_drive_label] else ''
            controller_key = None

            # When creating both IDE controller and CD/DVD drive at the same time we need the randomly
            # assigned (temporary) key of the newly created IDE controller
            if 'controller' in devices['cd'][cd_drive_label]:
                for spec in device_specs:
                    if spec.device.deviceInfo.label == devices['cd'][cd_drive_label]['controller']:
                        controller_key = spec.device.key
                        ide_controllers[controller_key] = 0
                        break
            else:
                for ide_controller_key, num_devices in six.iteritems(ide_controllers):
                    if num_devices < 2:
                        controller_key = ide_controller_key
                        break

            if not controller_key:
                log.error("No more available controllers for '{0}'. All IDE controllers are currently in use".format(cd_drive_label))
            else:
                cd_drive_spec = _add_new_cd_or_dvd_drive_helper(cd_drive_label, controller_key, device_type, mode, iso_path)
                device_specs.append(cd_drive_spec)
                ide_controllers[controller_key] += 1

    ret = {
        'device_specs': device_specs,
        'nics_map': nics_map
    }

    return ret