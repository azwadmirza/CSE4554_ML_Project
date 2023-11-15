def maybe_encode_nonstring_dtype(var, name=None):
    if 'dtype' in var.encoding and var.encoding['dtype'] != 'S1':
        dims, data, attrs, encoding = _var_as_tuple(var)
        dtype = np.dtype(encoding.pop('dtype'))
        if dtype != var.dtype:
            if np.issubdtype(dtype, np.integer):
                if (np.issubdtype(var.dtype, np.floating) and
                        '_FillValue' not in var.attrs):
                    warnings.warn('saving variable %s with floating '
                                  'point data as an integer dtype without '
                                  'any _FillValue to use for NaNs' % name,
                                  SerializationWarning, stacklevel=3)
                data = duck_array_ops.around(data)[...]
                if encoding.get('_Unsigned', False):
                    signed_dtype = np.dtype('i%s' % dtype.itemsize)
                    if '_FillValue' in var.attrs:
                        new_fill = signed_dtype.type(attrs['_FillValue'])
                        attrs['_FillValue'] = new_fill
                    data = data.astype(signed_dtype)
                    pop_to(encoding, attrs, '_Unsigned')
            data = data.astype(dtype=dtype)
        var = Variable(dims, data, attrs, encoding)
    return var