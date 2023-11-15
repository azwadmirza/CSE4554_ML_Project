def _format_instance_info(vm):
    device_full_info = {}
    for device in vm["config.hardware.device"]:
        device_full_info[device.deviceInfo.label] = {
            'key': device.key,
            'label': device.deviceInfo.label,
            'summary': device.deviceInfo.summary,
            'type': type(device).__name__.rsplit(".", 1)[1],
            'unitNumber': device.unitNumber
        }

        if hasattr(device.backing, 'network'):
            device_full_info[device.deviceInfo.label]['addressType'] = device.addressType
            device_full_info[device.deviceInfo.label]['macAddress'] = device.macAddress

        if hasattr(device, 'busNumber'):
            device_full_info[device.deviceInfo.label]['busNumber'] = device.busNumber

        if hasattr(device, 'device'):
            device_full_info[device.deviceInfo.label]['devices'] = device.device

        if hasattr(device, 'videoRamSizeInKB'):
            device_full_info[device.deviceInfo.label]['videoRamSizeInKB'] = device.videoRamSizeInKB

        if isinstance(device, vim.vm.device.VirtualDisk):
            device_full_info[device.deviceInfo.label]['capacityInKB'] = device.capacityInKB
            device_full_info[device.deviceInfo.label]['diskMode'] = device.backing.diskMode
            device_full_info[device.deviceInfo.label]['fileName'] = device.backing.fileName

    storage_full_info = {
        'committed': int(vm["summary.storage.committed"]),
        'uncommitted': int(vm["summary.storage.uncommitted"]),
        'unshared': int(vm["summary.storage.unshared"])
    }

    file_full_info = {}
    for file in vm["layoutEx.file"]:
        file_full_info[file.key] = {
            'key': file.key,
            'name': file.name,
            'size': file.size,
            'type': file.type
        }

    network_full_info = {}
    ip_addresses = []
    mac_addresses = []
    for net in vm["guest.net"]:
        network_full_info[net.network] = {
            'connected': net.connected,
            'ip_addresses': net.ipAddress,
            'mac_address': net.macAddress
        }
        ip_addresses.extend(net.ipAddress)
        mac_addresses.append(net.macAddress)

    vm_full_info = {
        'id': str(vm['name']),
        'image': "{0} (Detected)".format(vm["config.guestFullName"]),
        'size': u"cpu: {0}\nram: {1}MB".format(vm["config.hardware.numCPU"], vm["config.hardware.memoryMB"]),
        'state': str(vm["summary.runtime.powerState"]),
        'private_ips': ip_addresses,
        'public_ips': [],
        'devices': device_full_info,
        'storage': storage_full_info,
        'files': file_full_info,
        'guest_id': str(vm["config.guestId"]),
        'hostname': str(vm["object"].guest.hostName),
        'mac_address': mac_addresses,
        'networks': network_full_info,
        'path': str(vm["config.files.vmPathName"]),
        'tools_status': str(vm["guest.toolsStatus"]) if "guest.toolsStatus" in vm else "N/A"
    }

    return vm_full_info