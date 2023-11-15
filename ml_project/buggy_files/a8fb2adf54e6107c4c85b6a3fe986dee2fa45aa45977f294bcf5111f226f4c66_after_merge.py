def _is_linux_os(vm):
    os_type = None
    if vm and vm.storage_profile and vm.storage_profile.os_disk and vm.storage_profile.os_disk.os_type:
        os_type = vm.storage_profile.os_disk.os_type
    if os_type:
        return os_type.lower() == 'linux'
    # the os_type could be None for VM scaleset, let us check out os configurations
    if vm.os_profile.linux_configuration:
        return bool(vm.os_profile.linux_configuration)
    return False