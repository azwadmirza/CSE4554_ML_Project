def _manage_devices(devices, vm):
    unit_number = 0
    bus_number = 0
    device_specs = []
    existing_disks_label = []
    existing_scsi_adapters_label = []
    existing_network_adapters_label = []
    nics_map = []

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
                    size_gb = devices['disk'][device.deviceInfo.label]['size']
                    size_kb = int(size_gb) * 1024 * 1024
                    if device.capacityInKB < size_kb:
                        # expand the disk
                        disk_spec = _edit_existing_hard_disk_helper(device, size_kb)
                        device_specs.append(disk_spec)

        elif isinstance(device.backing, vim.vm.device.VirtualEthernetCard.NetworkBackingInfo) or isinstance(device.backing, vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo):
            # this is a network adapter
            if 'network' in list(devices.keys()):
                # there is atleast one network adapter specified to be created/configured
                existing_network_adapters_label.append(device.deviceInfo.label)
                if device.deviceInfo.label in list(devices['network'].keys()):
                    network_name = devices['network'][device.deviceInfo.label]['name']
                    switch_type = devices['network'][device.deviceInfo.label]['switch_type'] if 'switch_type' in devices['network'][device.deviceInfo.label] else ''
                    network_spec = _edit_existing_network_adapter_helper(device, network_name, switch_type)
                    adapter_mapping = _set_network_adapter_mapping_helper(devices['network'][device.deviceInfo.label])
                    device_specs.append(network_spec)
                    nics_map.append(adapter_mapping)

        elif hasattr(device, 'scsiCtlrUnitNumber'):
            # this is a scsi adapter
            if 'scsi' in list(devices.keys()):
                # there is atleast one scsi adapter specified to be created/configured
                bus_number += 1
                existing_scsi_adapters_label.append(device.deviceInfo.label)
                if device.deviceInfo.label in list(devices['scsi'].keys()):
                    # Modify the existing SCSI adapter
                    scsi_adapter_properties = devices['scsi'][device.deviceInfo.label]
                    bus_sharing = scsi_adapter_properties['bus_sharing'].strip().lower() if 'bus_sharing' in scsi_adapter_properties else None
                    if bus_sharing and bus_sharing in ['virtual', 'physical', 'no']:
                        bus_sharing = '{0}Sharing'.format(bus_sharing)
                        if bus_sharing != device.sharedBus:
                            # Only edit the SCSI adapter if bus_sharing is different
                            scsi_spec = _edit_existing_scsi_adapter_helper(device, bus_sharing)
                            device_specs.append(scsi_spec)

    if 'disk' in list(devices.keys()):
        disks_to_create = list(set(devices['disk'].keys()) - set(existing_disks_label))
        disks_to_create.sort()
        log.debug("Disks to create: {0}".format(disks_to_create))
        for disk_label in disks_to_create:
            # create the disk
            size_gb = devices['disk'][disk_label]['size']
            disk_spec = _add_new_hard_disk_helper(disk_label, size_gb, unit_number)
            device_specs.append(disk_spec)
            unit_number += 1

    if 'network' in list(devices.keys()):
        network_adapters_to_create = list(set(devices['network'].keys()) - set(existing_network_adapters_label))
        network_adapters_to_create.sort()
        log.debug("Networks to create: {0}".format(network_adapters_to_create))
        for network_adapter_label in network_adapters_to_create:
            network_name = devices['network'][network_adapter_label]['name']
            adapter_type = devices['network'][network_adapter_label]['adapter_type'] if 'adapter_type' in devices['network'][network_adapter_label] else ''
            switch_type = devices['network'][network_adapter_label]['switch_type'] if 'switch_type' in devices['network'][network_adapter_label] else ''
            # create the network adapter
            network_spec = _add_new_network_adapter_helper(network_adapter_label, network_name, adapter_type, switch_type)
            adapter_mapping = _set_network_adapter_mapping_helper(devices['network'][network_adapter_label])
            device_specs.append(network_spec)
            nics_map.append(adapter_mapping)

    if 'scsi' in list(devices.keys()):
        scsi_adapters_to_create = list(set(devices['scsi'].keys()) - set(existing_scsi_adapters_label))
        scsi_adapters_to_create.sort()
        log.debug("SCSI adapters to create: {0}".format(scsi_adapters_to_create))
        for scsi_adapter_label in scsi_adapters_to_create:
            # create the scsi adapter
            scsi_adapter_properties = devices['scsi'][scsi_adapter_label]
            scsi_spec = _add_new_scsi_adapter_helper(scsi_adapter_label, scsi_adapter_properties, bus_number)
            device_specs.append(scsi_spec)
            bus_number += 1

    ret = {
        'device_specs': device_specs,
        'nics_map': nics_map
    }

    return ret