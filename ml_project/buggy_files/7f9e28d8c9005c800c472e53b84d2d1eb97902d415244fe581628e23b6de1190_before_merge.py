def apply_ufunc(func, *args, **kwargs):
    """apply_ufunc(func : Callable,
                   *args : Any,
                   input_core_dims : Optional[Sequence[Sequence]] = None,
                   output_core_dims : Optional[Sequence[Sequence]] = ((),),
                   exclude_dims : Collection = frozenset(),
                   vectorize : bool = False,
                   join : str = 'exact',
                   dataset_join : str = 'exact',
                   dataset_fill_value : Any = _NO_FILL_VALUE,
                   keep_attrs : bool = False,
                   kwargs : Mapping = None,
                   dask : str = 'forbidden',
                   output_dtypes : Optional[Sequence] = None,
                   output_sizes : Optional[Mapping[Any, int]] = None)

    Apply a vectorized function for unlabeled arrays on xarray objects.

    The function will be mapped over the data variable(s) of the input
    arguments using xarray's standard rules for labeled computation, including
    alignment, broadcasting, looping over GroupBy/Dataset variables, and
    merging of coordinates.

    Parameters
    ----------
    func : callable
        Function to call like ``func(*args, **kwargs)`` on unlabeled arrays
        (``.data``) that returns an array or tuple of arrays. If multiple
        arguments with non-matching dimensions are supplied, this function is
        expected to vectorize (broadcast) over axes of positional arguments in
        the style of NumPy universal functions [1]_ (if this is not the case,
        set ``vectorize=True``). If this function returns multiple outputs, you
        must set ``output_core_dims`` as well.
    *args : Dataset, DataArray, GroupBy, Variable, numpy/dask arrays or scalars
        Mix of labeled and/or unlabeled arrays to which to apply the function.
    input_core_dims : Sequence[Sequence], optional
        List of the same length as ``args`` giving the list of core dimensions
        on each input argument that should not be broadcast. By default, we
        assume there are no core dimensions on any input arguments.

        For example, ``input_core_dims=[[], ['time']]`` indicates that all
        dimensions on the first argument and all dimensions other than 'time'
        on the second argument should be broadcast.

        Core dimensions are automatically moved to the last axes of input
        variables before applying ``func``, which facilitates using NumPy style
        generalized ufuncs [2]_.
    output_core_dims : List[tuple], optional
        List of the same length as the number of output arguments from
        ``func``, giving the list of core dimensions on each output that were
        not broadcast on the inputs. By default, we assume that ``func``
        outputs exactly one array, with axes corresponding to each broadcast
        dimension.

        Core dimensions are assumed to appear as the last dimensions of each
        output in the provided order.
    exclude_dims : set, optional
        Core dimensions on the inputs to exclude from alignment and
        broadcasting entirely. Any input coordinates along these dimensions
        will be dropped. Each excluded dimension must also appear in
        ``input_core_dims`` for at least one argument.
    vectorize : bool, optional
        If True, then assume ``func`` only takes arrays defined over core
        dimensions as input and vectorize it automatically with
        :py:func:`numpy.vectorize`. This option exists for convenience, but is
        almost always slower than supplying a pre-vectorized function.
        Using this option requires NumPy version 1.12 or newer.
    join : {'outer', 'inner', 'left', 'right', 'exact'}, optional
        Method for joining the indexes of the passed objects along each
        dimension, and the variables of Dataset objects with mismatched
        data variables:

        - 'outer': use the union of object indexes
        - 'inner': use the intersection of object indexes
        - 'left': use indexes from the first object with each dimension
        - 'right': use indexes from the last object with each dimension
        - 'exact': raise `ValueError` instead of aligning when indexes to be
          aligned are not equal
    dataset_join : {'outer', 'inner', 'left', 'right', 'exact'}, optional
        Method for joining variables of Dataset objects with mismatched
        data variables.

        - 'outer': take variables from both Dataset objects
        - 'inner': take only overlapped variables
        - 'left': take only variables from the first object
        - 'right': take only variables from the last object
        - 'exact': data variables on all Dataset objects must match exactly
    dataset_fill_value : optional
        Value used in place of missing variables on Dataset inputs when the
        datasets do not share the exact same ``data_vars``. Required if
        ``dataset_join not in {'inner', 'exact'}``, otherwise ignored.
    keep_attrs: boolean, Optional
        Whether to copy attributes from the first argument to the output.
    kwargs: dict, optional
        Optional keyword arguments passed directly on to call ``func``.
    dask: 'forbidden', 'allowed' or 'parallelized', optional
        How to handle applying to objects containing lazy data in the form of
        dask arrays:

        - 'forbidden' (default): raise an error if a dask array is encountered.
        - 'allowed': pass dask arrays directly on to ``func``.
        - 'parallelized': automatically parallelize ``func`` if any of the
          inputs are a dask array. If used, the ``output_dtypes`` argument must
          also be provided. Multiple output arguments are not yet supported.
    output_dtypes : list of dtypes, optional
        Optional list of output dtypes. Only used if dask='parallelized'.
    output_sizes : dict, optional
        Optional mapping from dimension names to sizes for outputs. Only used
        if dask='parallelized' and new dimensions (not found on inputs) appear
        on outputs.

    Returns
    -------
    Single value or tuple of Dataset, DataArray, Variable, dask.array.Array or
    numpy.ndarray, the first type on that list to appear on an input.

    Examples
    --------
    For illustrative purposes only, here are examples of how you could use
    ``apply_ufunc`` to write functions to (very nearly) replicate existing
    xarray functionality:

    Calculate the vector magnitude of two arguments::

        def magnitude(a, b):
            func = lambda x, y: np.sqrt(x ** 2 + y ** 2)
            return xr.apply_func(func, a, b)

    Compute the mean (``.mean``) over one dimension::

        def mean(obj, dim):
            # note: apply always moves core dimensions to the end
            return apply_ufunc(np.mean, obj,
                               input_core_dims=[[dim]],
                               kwargs={'axis': -1})

    Inner product over a specific dimension::

        def _inner(x, y):
            result = np.matmul(x[..., np.newaxis, :], y[..., :, np.newaxis])
            return result[..., 0, 0]

        def inner_product(a, b, dim):
            return apply_ufunc(_inner, a, b, input_core_dims=[[dim], [dim]])

    Stack objects along a new dimension (like ``xr.concat``)::

        def stack(objects, dim, new_coord):
            # note: this version does not stack coordinates
            func = lambda *x: np.stack(x, axis=-1)
            result = apply_ufunc(func, *objects,
                                 output_core_dims=[[dim]],
                                 join='outer',
                                 dataset_fill_value=np.nan)
            result[dim] = new_coord
            return result

    If your function is not vectorized but can be applied only to core
    dimensions, you can use ``vectorize=True`` to turn into a vectorized
    function. This wraps :py:func:`numpy.vectorize`, so the operation isn't
    terribly fast. Here we'll use it to calculate the distance between
    empirical samples from two probability distributions, using a scipy
    function that needs to be applied to vectors::

        import scipy.stats

        def earth_mover_distance(first_samples,
                                 second_samples,
                                 dim='ensemble'):
            return apply_ufunc(scipy.stats.wasserstein_distance,
                               first_samples, second_samples,
                               input_core_dims=[[dim], [dim]],
                               vectorize=True)

    Most of NumPy's builtin functions already broadcast their inputs
    appropriately for use in `apply`. You may find helper functions such as
    numpy.broadcast_arrays helpful in writing your function. `apply_ufunc` also
    works well with numba's vectorize and guvectorize. Further explanation with
    examples are provided in the xarray documentation [3].

    See also
    --------
    numpy.broadcast_arrays
    numba.vectorize
    numba.guvectorize

    References
    ----------
    .. [1] http://docs.scipy.org/doc/numpy/reference/ufuncs.html
    .. [2] http://docs.scipy.org/doc/numpy/reference/c-api.generalized-ufuncs.html
    .. [3] http://xarray.pydata.org/en/stable/computation.html#wrapping-custom-computation
    """  # noqa: E501  # don't error on that URL one line up
    from .groupby import GroupBy
    from .dataarray import DataArray
    from .variable import Variable

    input_core_dims = kwargs.pop('input_core_dims', None)
    output_core_dims = kwargs.pop('output_core_dims', ((),))
    vectorize = kwargs.pop('vectorize', False)
    join = kwargs.pop('join', 'exact')
    dataset_join = kwargs.pop('dataset_join', 'exact')
    keep_attrs = kwargs.pop('keep_attrs', False)
    exclude_dims = kwargs.pop('exclude_dims', frozenset())
    dataset_fill_value = kwargs.pop('dataset_fill_value', _NO_FILL_VALUE)
    kwargs_ = kwargs.pop('kwargs', None)
    dask = kwargs.pop('dask', 'forbidden')
    output_dtypes = kwargs.pop('output_dtypes', None)
    output_sizes = kwargs.pop('output_sizes', None)
    if kwargs:
        raise TypeError('apply_ufunc() got unexpected keyword arguments: %s'
                        % list(kwargs))

    if input_core_dims is None:
        input_core_dims = ((),) * (len(args))

    signature = _UFuncSignature(input_core_dims, output_core_dims)

    if exclude_dims and not exclude_dims <= signature.all_core_dims:
        raise ValueError('each dimension in `exclude_dims` must also be a '
                         'core dimension in the function signature')

    if kwargs_:
        func = functools.partial(func, **kwargs_)

    if vectorize:
        if signature.all_core_dims:
            # we need the signature argument
            if LooseVersion(np.__version__) < '1.12':  # pragma: no cover
                raise NotImplementedError(
                    'numpy 1.12 or newer required when using vectorize=True '
                    'in xarray.apply_ufunc with non-scalar output core '
                    'dimensions.')
            func = np.vectorize(func,
                                otypes=output_dtypes,
                                signature=signature.to_gufunc_string(),
                                excluded=set(kwargs))
        else:
            func = np.vectorize(func,
                                otypes=output_dtypes,
                                excluded=set(kwargs))

    variables_ufunc = functools.partial(apply_variable_ufunc, func,
                                        signature=signature,
                                        exclude_dims=exclude_dims,
                                        keep_attrs=keep_attrs,
                                        dask=dask,
                                        output_dtypes=output_dtypes,
                                        output_sizes=output_sizes)

    if any(isinstance(a, GroupBy) for a in args):
        # kwargs has already been added into func
        this_apply = functools.partial(apply_ufunc, func,
                                       input_core_dims=input_core_dims,
                                       output_core_dims=output_core_dims,
                                       exclude_dims=exclude_dims,
                                       join=join,
                                       dataset_join=dataset_join,
                                       dataset_fill_value=dataset_fill_value,
                                       keep_attrs=keep_attrs,
                                       dask=dask)
        return apply_groupby_ufunc(this_apply, *args)
    elif any(is_dict_like(a) for a in args):
        return apply_dataset_ufunc(variables_ufunc, *args,
                                   signature=signature,
                                   join=join,
                                   exclude_dims=exclude_dims,
                                   fill_value=dataset_fill_value,
                                   dataset_join=dataset_join,
                                   keep_attrs=keep_attrs)
    elif any(isinstance(a, DataArray) for a in args):
        return apply_dataarray_ufunc(variables_ufunc, *args,
                                     signature=signature,
                                     join=join,
                                     exclude_dims=exclude_dims)
    elif any(isinstance(a, Variable) for a in args):
        return variables_ufunc(*args)
    else:
        return apply_array_ufunc(func, *args, dask=dask)