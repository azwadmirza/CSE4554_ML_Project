def _apply_with_dask_atop(func, args, input_dims, output_dims, signature,
                          output_dtypes, output_sizes=None):
    import dask.array as da

    if signature.num_outputs > 1:
        raise NotImplementedError('multiple outputs from apply_ufunc not yet '
                                  "supported with dask='parallelized'")

    if output_dtypes is None:
        raise ValueError('output dtypes (output_dtypes) must be supplied to '
                         "apply_func when using dask='parallelized'")
    if not isinstance(output_dtypes, list):
        raise TypeError('output_dtypes must be a list of objects coercible to '
                        'numpy dtypes, got {}'.format(output_dtypes))
    if len(output_dtypes) != signature.num_outputs:
        raise ValueError('apply_ufunc arguments output_dtypes and '
                         'output_core_dims must have the same length: {} vs {}'
                         .format(len(output_dtypes), signature.num_outputs))
    (dtype,) = output_dtypes

    if output_sizes is None:
        output_sizes = {}

    new_dims = signature.all_output_core_dims - signature.all_input_core_dims
    if any(dim not in output_sizes for dim in new_dims):
        raise ValueError("when using dask='parallelized' with apply_ufunc, "
                         'output core dimensions not found on inputs must have '
                         'explicitly set sizes with ``output_sizes``: {}'
                         .format(new_dims))

    for n, (data, core_dims) in enumerate(
            zip(args, signature.input_core_dims)):
        if isinstance(data, dask_array_type):
            # core dimensions cannot span multiple chunks
            for axis, dim in enumerate(core_dims, start=-len(core_dims)):
                if len(data.chunks[axis]) != 1:
                    raise ValueError(
                        'dimension {!r} on {}th function argument to '
                        "apply_ufunc with dask='parallelized' consists of "
                        'multiple chunks, but is also a core dimension. To '
                        'fix, rechunk into a single dask array chunk along '
                        'this dimension, i.e., ``.rechunk({})``, but beware '
                        'that this may significantly increase memory usage.'
                        .format(dim, n, {dim: -1}))

    (out_ind,) = output_dims
    # skip leading dimensions that we did not insert with broadcast_compat_data
    atop_args = [element
                 for (arg, dims) in zip(args, input_dims)
                 for element in (arg, dims[-getattr(arg, 'ndim', 0):])]
    return da.atop(func, out_ind, *atop_args, dtype=dtype, concatenate=True,
                   new_axes=output_sizes)