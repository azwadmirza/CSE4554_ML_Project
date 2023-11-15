def avail_images(call=None):
    '''
    Return a list of all the templates present in this VMware environment with basic
    details

    CLI Example:

    .. code-block:: bash

        salt-cloud --list-images my-vmware-config
    '''
    if call == 'action':
        raise SaltCloudSystemExit(
            'The avail_images function must be called with '
            '-f or --function, or with the --list-images option.'
        )

    templates = {}
    vm_properties = [
        "name",
        "config.template",
        "config.guestFullName",
        "config.hardware.numCPU",
        "config.hardware.memoryMB"
    ]

    vm_list = _get_mors_with_properties(vim.VirtualMachine, vm_properties)

    for vm in vm_list:
        if "config.template" in vm and vm["config.template"]:
            templates[vm["name"]] = {
                'name': vm["name"],
                'guest_fullname': vm["config.guestFullName"] if "config.guestFullName" in vm else "N/A",
                'cpus': vm["config.hardware.numCPU"] if "config.hardware.numCPU" in vm else "N/A",
                'ram': vm["config.hardware.memoryMB"] if "config.hardware.memoryMB" in vm else "N/A"
            }

    return templates