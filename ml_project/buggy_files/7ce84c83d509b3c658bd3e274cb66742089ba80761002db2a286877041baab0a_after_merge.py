def apply_variable_ufunc(func, *args, **kwargs):
    """apply_variable_ufunc(func, *args, signature, exclude_dims=frozenset())
    """
    from .variable import Variable, as_compatible_data

    signature = kwargs.pop('signature')
    exclude_dims = kwargs.pop('exclude_dims', _DEFAULT_FROZEN_SET)
    dask = kwargs.pop('dask', 'forbidden')
    output_dtypes = kwargs.pop('output_dtypes', None)
    output_sizes = kwargs.pop('output_sizes', None)
    keep_attrs = kwargs.pop('keep_attrs', False)
    if kwargs:
        raise TypeError('apply_variable_ufunc() got unexpected keyword '
                        'arguments: %s' % list(kwargs))

    dim_sizes = unified_dim_sizes((a for a in args if hasattr(a, 'dims')),
                                  exclude_dims=exclude_dims)
    broadcast_dims = tuple(dim for dim in dim_sizes
                           if dim not in signature.all_core_dims)
    output_dims = [broadcast_dims + out for out in signature.output_core_dims]

    input_data = [broadcast_compat_data(arg, broadcast_dims, core_dims)
                  if isinstance(arg, Variable)
                  else arg
                  for arg, core_dims in zip(args, signature.input_core_dims)]

    if any(isinstance(array, dask_array_type) for array in input_data):
        if dask == 'forbidden':
            raise ValueError('apply_ufunc encountered a dask array on an '
                             'argument, but handling for dask arrays has not '
                             'been enabled. Either set the ``dask`` argument '
                             'or load your data into memory first with '
                             '``.load()`` or ``.compute()``')
        elif dask == 'parallelized':
            input_dims = [broadcast_dims + dims
                          for dims in signature.input_core_dims]
            numpy_func = func

            def func(*arrays):
                return _apply_with_dask_atop(
                    numpy_func, arrays, input_dims, output_dims,
                    signature, output_dtypes, output_sizes)
        elif dask == 'allowed':
            pass
        else:
            raise ValueError('unknown setting for dask array handling in '
                             'apply_ufunc: {}'.format(dask))
    result_data = func(*input_data)

    if signature.num_outputs == 1:
        result_data = (result_data,)
    elif (not isinstance(result_data, tuple) or
            len(result_data) != signature.num_outputs):
        raise ValueError('applied function does not have the number of '
                         'outputs specified in the ufunc signature. '
                         'Result is not a tuple of {} elements: {!r}'
                         .format(signature.num_outputs, result_data))

    output = []
    for dims, data in zip(output_dims, result_data):
        data = as_compatible_data(data)
        if data.ndim != len(dims):
            raise ValueError(
                'applied function returned data with unexpected '
                'number of dimensions: {} vs {}, for dimensions {}'
                .format(data.ndim, len(dims), dims))

        var = Variable(dims, data, fastpath=True)
        for dim, new_size in var.sizes.items():
            if dim in dim_sizes and new_size != dim_sizes[dim]:
                raise ValueError(
                    'size of dimension {!r} on inputs was unexpectedly '
                    'changed by applied function from {} to {}. Only '
                    'dimensions specified in ``exclude_dims`` with '
                    'xarray.apply_ufunc are allowed to change size.'
                    .format(dim, dim_sizes[dim], new_size))

        if keep_attrs and isinstance(args[0], Variable):
            var.attrs.update(args[0].attrs)
        output.append(var)

    if signature.num_outputs == 1:
        return output[0]
    else:
        return tuple(output)