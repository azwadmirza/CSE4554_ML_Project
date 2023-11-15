def get_size(conn, vm_):
    """
    Return the VM's size object
    """
    sizes = conn.list_sizes()
    vm_size = config.get_cloud_config_value("size", vm_, __opts__)
    if not vm_size:
        return sizes[0]

    for size in sizes:
        if vm_size and str(vm_size) in (str(size.id), str(size.name),):
            return size
    raise SaltCloudNotFound(
        "The specified size, '{}', could not be found.".format(vm_size)
    )