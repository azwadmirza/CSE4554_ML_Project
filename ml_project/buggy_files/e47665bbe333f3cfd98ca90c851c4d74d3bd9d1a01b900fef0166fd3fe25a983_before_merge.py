def _add_new_ide_controller_helper(ide_controller_label, properties, bus_number):
    '''
    Helper function for adding new IDE controllers

    .. versionadded:: 2016.3.0
    '''
    random_key = randint(-200, -250)

    ide_spec = vim.vm.device.VirtualDeviceSpec()
    ide_spec.device = vim.vm.device.VirtualIDEController()

    ide_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add

    ide_spec.device.key = random_key
    ide_spec.device.busNumber = bus_number
    ide_spec.device.deviceInfo = vim.Description()
    ide_spec.device.deviceInfo.label = ide_controller_label
    ide_spec.device.deviceInfo.summary = ide_controller_label

    return ide_spec