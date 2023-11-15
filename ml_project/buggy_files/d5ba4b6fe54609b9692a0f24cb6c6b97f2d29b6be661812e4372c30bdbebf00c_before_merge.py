def _create_field_data(field, data_shape, land_mask):
    """
    Modifies a field's ``_data`` attribute either by:
     * converting DeferredArrayBytes into a lazy array,
     * converting LoadedArrayBytes into an actual numpy array.

    """
    if isinstance(field.core_data(), LoadedArrayBytes):
        loaded_bytes = field.core_data()
        field.data = _data_bytes_to_shaped_array(loaded_bytes.bytes,
                                                 field.lbpack,
                                                 field.boundary_packing,
                                                 data_shape,
                                                 loaded_bytes.dtype,
                                                 field.bmdi, land_mask)
    else:
        # Wrap the reference to the data payload within a data proxy
        # in order to support deferred data loading.
        fname, position, n_bytes, dtype = field.core_data()
        proxy = PPDataProxy(data_shape, dtype,
                            fname, position, n_bytes,
                            field.raw_lbpack,
                            field.boundary_packing,
                            field.bmdi, land_mask)
        block_shape = data_shape if 0 not in data_shape else (1, 1)
        field.data = as_lazy_data(proxy, chunks=block_shape)