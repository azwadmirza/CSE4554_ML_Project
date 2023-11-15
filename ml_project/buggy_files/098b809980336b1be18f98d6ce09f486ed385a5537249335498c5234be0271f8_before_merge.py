def _nc4_dtype(var):
    if var.dtype.kind == 'U':
        dtype = str
    elif var.dtype.kind in ['i', 'u', 'f', 'c', 'S']:
        dtype = var.dtype
    else:
        raise ValueError('cannot infer dtype for netCDF4 variable')
    return dtype