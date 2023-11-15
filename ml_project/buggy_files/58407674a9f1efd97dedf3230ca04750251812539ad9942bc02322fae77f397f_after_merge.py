def _format_instance_info(vm):
    device_full_info = {}

    if "config.hardware.device" in vm:
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
        'committed': int(vm["summary.storage.committed"]) if "summary.storage.committed" in vm else "N/A",
        'uncommitted': int(vm["summary.storage.uncommitted"]) if "summary.storage.uncommitted" in vm else "N/A",
        'unshared': int(vm["summary.storage.unshared"]) if "summary.storage.unshared" in vm else "N/A"
    }

    file_full_info = {}
    if "layoutEx.file" in vm:
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
    if "guest.net" in vm:
        for net in vm["guest.net"]:
            network_full_info[net.network] = {
                'connected': net.connected,
                'ip_addresses': net.ipAddress,
                'mac_address': net.macAddress
            }
            ip_addresses.extend(net.ipAddress)
            mac_addresses.append(net.macAddress)

    cpu = vm["config.hardware.numCPU"] if "config.hardware.numCPU" in vm else "N/A"
    ram = "{0} MB".format(vm["config.hardware.memoryMB"]) if "config.hardware.memoryMB" in vm else "N/A"
    vm_full_info = {
        'id': str(vm['name']),
        'image': "{0} (Detected)".format(vm["config.guestFullName"]) if "config.guestFullName" in vm else "N/A",
        'size': u"cpu: {0}\nram: {1}".format(cpu, ram),
        'state': str(vm["summary.runtime.powerState"]) if "summary.runtime.powerState" in vm else "N/A",
        'private_ips': ip_addresses,
        'public_ips': [],
        'devices': device_full_info,
        'storage': storage_full_info,
        'files': file_full_info,
        'guest_id': str(vm["config.guestId"]) if "config.guestId" in vm else "N/A",
        'hostname': str(vm["object"].guest.hostName),
        'mac_address': mac_addresses,
        'networks': network_full_info,
        'path': str(vm["config.files.vmPathName"]) if "config.files.vmPathName" in vm else "N/A",
        'tools_status': str(vm["guest.toolsStatus"]) if "guest.toolsStatus" in vm else "N/A"
    }

    return vm_full_info