def dataset_repr(ds):
    summary = ['<xarray.%s>' % type(ds).__name__]

    col_width = _calculate_col_width(ds)

    dims_start = pretty_print('Dimensions:', col_width)
    all_dim_strings = ['%s: %s' % (k, v) for k, v in iteritems(ds.dims)]
    summary.append('%s(%s)' % (dims_start, ', '.join(all_dim_strings)))

    summary.append(coords_repr(ds.coords, col_width=col_width))
    summary.append(vars_repr(ds.data_vars, col_width=col_width))
    if ds.attrs:
        summary.append(attrs_repr(ds.attrs))

    return '\n'.join(summary)