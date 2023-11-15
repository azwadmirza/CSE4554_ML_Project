def _create_field_data(field, data_shape, land_mask_field=None):
    """
    Modifies a field's ``_data`` attribute either by:
     * converting a 'deferred array bytes' tuple into a lazy array,
     * converting LoadedArrayBytes into an actual numpy array.

    If 'land_mask_field' is passed (not None), then it contains the associated
    landmask, which is also a field :  Its data array is used as a template for
    `field`'s data, determining its size, shape and the locations of all the
    valid (non-missing) datapoints.

    """
    if isinstance(field.core_data(), LoadedArrayBytes):
        loaded_bytes = field.core_data()
        field.data = _data_bytes_to_shaped_array(loaded_bytes.bytes,
                                                 field.lbpack,
                                                 field.boundary_packing,
                                                 data_shape,
                                                 loaded_bytes.dtype,
                                                 field.bmdi,
                                                 land_mask_field)
    else:
        # Wrap the reference to the data payload within a data proxy
        # in order to support deferred data loading.
        fname, position, n_bytes, dtype = field.core_data()
        proxy = PPDataProxy(data_shape, dtype,
                            fname, position, n_bytes,
                            field.raw_lbpack,
                            field.boundary_packing,
                            field.bmdi)
        block_shape = data_shape if 0 not in data_shape else (1, 1)
        if land_mask_field is None:
            # For a "normal" (non-landsea-masked) field, the proxy can be
            # wrapped directly as a deferred array.
            field.data = as_lazy_data(proxy, chunks=block_shape)
        else:
            # This is a landsea-masked field, and its data must be handled in
            # a different way :  Because data shape/size is not known in
            # advance, the data+mask calculation can't be represented
            # as a dask-array operation.  Instead, we make that calculation
            # 'delayed', and then use 'from_delayed' to make the result back
            # into a dask array -- because the final result shape *is* known.
            @dask.delayed
            def fetch_valid_values_array():
                # Return the data values array (shape+size unknown).
                return proxy[:]

            delayed_valid_values = fetch_valid_values_array()

            # Get the mask data-array from the landsea-mask field.
            # This is *either* a lazy or a real array, we don't actually care.
            # If this is a deferred dependency, the delayed calc can see that.
            mask_field_array = land_mask_field.core_data()

            # Check whether this field uses a land or a sea mask.
            if field.lbpack.n3 not in (1, 2):
                raise ValueError('Unsupported mask compression : '
                                 'lbpack.n3 = {}.'.format(field.lbpack.n3))
            if field.lbpack.n3 == 2:
                # Sea-mask packing : points are inverse of the land-mask.
                mask_field_array = ~mask_field_array

            # Define the mask+data calculation as a deferred operation.
            # NOTE: duplicates the operation in _data_bytes_to_shaped_array.
            @dask.delayed
            def calc_array(mask, values):
                # Note: "mask" is True at *valid* points, not missing ones.
                # First ensure the mask array is boolean (not int).
                mask = mask.astype(bool)
                result = ma.masked_all(mask.shape, dtype=dtype)
                # Apply the fill-value from the proxy object.
                # Note: 'values' is just 'proxy' in a dask wrapper.  This arg
                # must be a dask type so that 'delayed' can recognise it, but
                # that provides no access to the underlying fill value.
                result.fill_value = proxy.mdi
                n_values = np.sum(mask)
                if n_values > 0:
                    # Note: data field can have excess values, but not fewer.
                    result[mask] = values[:n_values]
                return result

            delayed_result = calc_array(mask_field_array,
                                        delayed_valid_values)
            lazy_result_array = da.from_delayed(delayed_result,
                                                shape=block_shape,
                                                dtype=dtype)
            field.data = lazy_result_array