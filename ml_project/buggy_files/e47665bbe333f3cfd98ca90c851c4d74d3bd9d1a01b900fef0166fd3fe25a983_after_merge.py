def _add_new_ide_controller_helper(ide_controller_label, controller_key, bus_number):
    '''
    Helper function for adding new IDE controllers

    .. versionadded:: 2016.3.0

    Args:
      ide_controller_label: label of the IDE controller
      controller_key: if not None, the controller key to use; otherwise it is randomly generated
      bus_number: bus number

    Returns: created device spec for an IDE controller

    '''
    if controller_key is None:
        controller_key = randint(-200, 250)

    ide_spec = vim.vm.device.VirtualDeviceSpec()
    ide_spec.device = vim.vm.device.VirtualIDEController()

    ide_spec.operation = vim.vm.device.VirtualDeviceSpec.Operation.add

    ide_spec.device.key = controller_key
    ide_spec.device.busNumber = bus_number
    ide_spec.device.deviceInfo = vim.Description()
    ide_spec.device.deviceInfo.label = ide_controller_label
    ide_spec.device.deviceInfo.summary = ide_controller_label

    return ide_spec