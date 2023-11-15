def _is_linux_os(vm):
    os_type = vm.storage_profile.os_disk.os_type if vm.storage_profile.os_disk.os_type else None
    if os_type:
        return os_type.lower() == 'linux'
    # the os_type could be None for VM scaleset, let us check out os configurations
    if vm.os_profile.linux_configuration:
        return bool(vm.os_profile.linux_configuration)
    return False