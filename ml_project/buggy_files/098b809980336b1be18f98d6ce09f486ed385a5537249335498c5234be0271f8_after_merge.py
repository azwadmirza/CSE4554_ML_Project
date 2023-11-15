def _nc4_dtype(var):
    if coding.strings.is_unicode_dtype(var.dtype):
        dtype = str
    elif var.dtype.kind in ['i', 'u', 'f', 'c', 'S']:
        dtype = var.dtype
    else:
        raise ValueError('unsupported dtype for netCDF4 variable: {}'
                         .format(var.dtype))
    return dtype