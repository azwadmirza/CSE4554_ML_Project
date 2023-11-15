def device_memory_size(devmem):
    """Check the memory size of the device memory.
    The result is cached in the device memory object.
    It may query the driver for the memory size of the device memory allocation.
    """
    sz = getattr(devmem, '_cuda_memsize_', None)
    if sz is None:
        s, e = device_extents(devmem)
        sz = e - s
        devmem._cuda_memsize_ = sz
    assert sz >= 0, "{} length array".format(sz)
    return sz