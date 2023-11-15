def from_cuda_array_interface(desc, owner=None):
    """Create a DeviceNDArray from a cuda-array-interface description.
    The *owner* is the owner of the underlying memory.
    The resulting DeviceNDArray will acquire a reference from it.
    """
    shape = desc['shape']
    strides = desc.get('strides')
    dtype = np.dtype(desc['typestr'])

    shape, strides, dtype = _prepare_shape_strides_dtype(
        shape, strides, dtype, order='C')
    size = driver.memory_size_from_info(shape, strides, dtype.itemsize)

    devptr = driver.get_devptr_for_active_ctx(desc['data'][0])
    data = driver.MemoryPointer(
        current_context(), devptr, size=size, owner=owner)
    da = devicearray.DeviceNDArray(shape=shape, strides=strides,
                                   dtype=dtype, gpu_data=data)
    return da