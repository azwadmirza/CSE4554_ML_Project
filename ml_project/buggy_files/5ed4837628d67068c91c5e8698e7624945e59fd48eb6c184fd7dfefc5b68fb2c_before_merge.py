def _format_instance_info_select(vm, selection):
    vm_select_info = {}

    if 'id' in selection:
        vm_select_info['id'] = vm["name"]

    if 'image' in selection:
        vm_select_info['image'] = "{0} (Detected)".format(vm["config.guestFullName"])

    if 'size' in selection:
        vm_select_info['size'] = u"cpu: {0}\nram: {1}MB".format(vm["config.hardware.numCPU"], vm["config.hardware.memoryMB"])

    if 'state' in selection:
        vm_select_info['state'] = str(vm["summary.runtime.powerState"])

    if 'guest_id' in selection:
        vm_select_info['guest_id'] = vm["config.guestId"]

    if 'hostname' in selection:
        vm_select_info['hostname'] = vm["object"].guest.hostName

    if 'path' in selection:
        vm_select_info['path'] = vm["config.files.vmPathName"]

    if 'tools_status' in selection:
        vm_select_info['tools_status'] = str(vm["guest.toolsStatus"]) if "guest.toolsStatus" in vm else "N/A"

    if ('private_ips' or 'mac_address' or 'networks') in selection:
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

        if 'private_ips' in selection:
            vm_select_info['private_ips'] = ip_addresses

        if 'mac_address' in selection:
            vm_select_info['mac_address'] = mac_addresses

        if 'networks' in selection:
            vm_select_info['networks'] = network_full_info

    if 'devices' in selection:
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

        vm_select_info['devices'] = device_full_info

    if 'storage' in selection:
        storage_full_info = {
            'committed': vm["summary.storage.committed"],
            'uncommitted': vm["summary.storage.uncommitted"],
            'unshared': vm["summary.storage.unshared"]
        }
        vm_select_info['storage'] = storage_full_info

    if 'files' in selection:
        file_full_info = {}
        for file in vm["layoutEx.file"]:
            file_full_info[file.key] = {
                'key': file.key,
                'name': file.name,
                'size': file.size,
                'type': file.type
            }
        vm_select_info['files'] = file_full_info

    return vm_select_info