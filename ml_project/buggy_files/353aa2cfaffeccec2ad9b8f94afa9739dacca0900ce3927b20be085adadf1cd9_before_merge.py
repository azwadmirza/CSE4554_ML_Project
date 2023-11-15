def list_nodes(kwargs=None, call=None):
    '''
    Return a list of all VMs and templates that are on the specified provider, with basic fields

    CLI Example:

    .. code-block:: bash

        salt-cloud -f list_nodes my-vmware-config

    To return a list of all VMs and templates present on ALL configured providers, with basic
    fields:

    CLI Example:

    .. code-block:: bash

        salt-cloud -Q
    '''
    if call == 'action':
        raise SaltCloudSystemExit(
            'The list_nodes function must be called '
            'with -f or --function.'
        )

    ret = {}
    vm_properties = [
        "name",
        "guest.ipAddress",
        "config.guestFullName",
        "config.hardware.numCPU",
        "config.hardware.memoryMB",
        "summary.runtime.powerState"
    ]

    vm_list = _get_mors_with_properties(vim.VirtualMachine, vm_properties)

    for vm in vm_list:
        vm_info = {
            'id': vm["name"],
            'image': "{0} (Detected)".format(vm["config.guestFullName"]),
            'size': u"cpu: {0}\nram: {1}MB".format(vm["config.hardware.numCPU"], vm["config.hardware.memoryMB"]),
            'state': str(vm["summary.runtime.powerState"]),
            'private_ips': [vm["guest.ipAddress"]] if "guest.ipAddress" in vm else [],
            'public_ips': []
        }
        ret[vm_info['id']] = vm_info

    return ret