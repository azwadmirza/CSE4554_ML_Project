def array_repr(arr):
    # used for DataArray, Variable and Coordinate
    if hasattr(arr, 'name') and arr.name is not None:
        name_str = '%r ' % arr.name
    else:
        name_str = ''
    dim_summary = ', '.join('%s: %s' % (k, v) for k, v
                            in zip(arr.dims, arr.shape))

    summary = ['<xarray.%s %s(%s)>'
               % (type(arr).__name__, name_str, dim_summary)]

    if isinstance(getattr(arr, 'variable', arr)._data, dask_array_type):
        summary.append(repr(arr.data))
    elif arr._in_memory or arr.size < 1e5:
        summary.append(repr(arr.values))
    else:
        summary.append('[%s values with dtype=%s]' % (arr.size, arr.dtype))

    if hasattr(arr, 'coords'):
        if arr.coords:
            summary.append(repr(arr.coords))

    if arr.attrs:
        summary.append(attrs_repr(arr.attrs))

    return '\n'.join(summary)