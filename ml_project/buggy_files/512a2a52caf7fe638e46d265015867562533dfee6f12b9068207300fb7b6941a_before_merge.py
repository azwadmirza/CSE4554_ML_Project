def as_variable(obj, name=None):
    """Convert an object into a Variable.

    Parameters
    ----------
    obj : object
        Object to convert into a Variable.

        - If the object is already a Variable, return a shallow copy.
        - Otherwise, if the object has 'dims' and 'data' attributes, convert
          it into a new Variable.
        - If all else fails, attempt to convert the object into a Variable by
          unpacking it into the arguments for creating a new Variable.
    name : str, optional
        If provided:

        - `obj` can be a 1D array, which is assumed to label coordinate values
          along a dimension of this given name.
        - Variables with name matching one of their dimensions are converted
          into `IndexVariable` objects.

    Returns
    -------
    var : Variable
        The newly created variable.

    """
    # TODO: consider extending this method to automatically handle Iris and
    # pandas objects.
    if hasattr(obj, 'variable'):
        # extract the primary Variable from DataArrays
        obj = obj.variable

    if isinstance(obj, Variable):
        obj = obj.copy(deep=False)
    elif hasattr(obj, 'dims') and (hasattr(obj, 'data') or
                                   hasattr(obj, 'values')):
        obj_data = getattr(obj, 'data', None)
        if obj_data is None:
            obj_data = getattr(obj, 'values')
        obj = Variable(obj.dims, obj_data,
                       getattr(obj, 'attrs', None),
                       getattr(obj, 'encoding', None))
    elif isinstance(obj, tuple):
        try:
            obj = Variable(*obj)
        except TypeError:
            # use .format() instead of % because it handles tuples consistently
            raise TypeError('tuples to convert into variables must be of the '
                            'form (dims, data[, attrs, encoding]): '
                            '{}'.format(obj))
    elif utils.is_scalar(obj):
        obj = Variable([], obj)
    elif getattr(obj, 'name', None) is not None:
        obj = Variable(obj.name, obj)
    elif name is not None:
        data = as_compatible_data(obj)
        if data.ndim != 1:
            raise MissingDimensionsError(
                'cannot set variable %r with %r-dimensional data '
                'without explicit dimension names. Pass a tuple of '
                '(dims, data) instead.' % (name, data.ndim))
        obj = Variable(name, obj, fastpath=True)
    else:
        raise TypeError('unable to convert object into a variable without an '
                        'explicit list of dimensions: %r' % obj)

    if name is not None and name in obj.dims:
        # convert the Variable into an Index
        if obj.ndim != 1:
            raise MissingDimensionsError(
                '%r has more than 1-dimension and the same name as one of its '
                'dimensions %r. xarray disallows such variables because they '
                'conflict with the coordinates used to label '
                'dimensions.' % (name, obj.dims))
        obj = obj.to_index_variable()

    return obj