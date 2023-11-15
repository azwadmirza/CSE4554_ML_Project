def _edit_existing_network_adapter_helper(network_adapter, new_network_name, switch_type):
    switch_type.strip().lower()
    if switch_type == 'standard':
        network_ref = _get_mor_by_property(vim.Network, new_network_name)
        network_adapter.backing.deviceName = new_network_name
        network_adapter.backing.network = network_ref
    elif switch_type == 'distributed':
        network_ref = _get_mor_by_property(vim.dvs.DistributedVirtualPortgroup, new_network_name)
        dvs_port_connection = vim.dvs.PortConnection(
            portgroupKey=network_ref.key,
            switchUuid=network_ref.config.distributedVirtualSwitch.uuid
        )
        network_adapter.backing = vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
        network_adapter.backing.port = dvs_port_connection
    else:
        # If switch type not specified or does not match, show error and return
        if not switch_type:
            err_msg = "The switch type to be used by {0} has not been specified".format(network_adapter.deviceInfo.label)
        else:
            err_msg = "Cannot create {0}. Invalid/unsupported switch type {1}".format(network_adapter.deviceInfo.label, switch_type)
        raise SaltCloudSystemExit(err_msg)

    network_adapter.deviceInfo.summary = new_network_name
    network_adapter.connectable.allowGuestControl = True
    network_adapter.connectable.startConnected = True
    network_spec = vim.vm.device.VirtualDeviceSpec()
    network_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.edit
    network_spec.device = network_adapter

    return network_spec