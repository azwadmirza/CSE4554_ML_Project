def select(condlist, choicelist, default=0):
    """
    Return an array drawn from elements in choicelist, depending on conditions.

    Parameters
    ----------
    condlist : list of bool ndarrays
        The list of conditions which determine from which array in `choicelist`
        the output elements are taken. When multiple conditions are satisfied,
        the first one encountered in `condlist` is used.
    choicelist : list of ndarrays
        The list of arrays from which the output elements are taken. It has
        to be of the same length as `condlist`.
    default : scalar, optional
        The element inserted in `output` when all conditions evaluate to False.

    Returns
    -------
    output : ndarray
        The output at position m is the m-th element of the array in
        `choicelist` where the m-th element of the corresponding array in
        `condlist` is True.

    See Also
    --------
    where : Return elements from one of two arrays depending on condition.
    take, choose, compress, diag, diagonal

    Examples
    --------
    >>> x = np.arange(10)
    >>> condlist = [x<3, x>5]
    >>> choicelist = [x, x**2]
    >>> np.select(condlist, choicelist)
    array([ 0,  1,  2,  0,  0,  0, 36, 49, 64, 81])

    """
    # Check the size of condlist and choicelist are the same, or abort.
    if len(condlist) != len(choicelist):
        raise ValueError(
            'list of cases must be same length as list of conditions')

    # Now that the dtype is known, handle the deprecated select([], []) case
    if len(condlist) == 0:
        warnings.warn("select with an empty condition list is not possible"
                      "and will be deprecated",
                      DeprecationWarning)
        return np.asarray(default)[()]

    choicelist = [np.asarray(choice) for choice in choicelist]
    choicelist.append(np.asarray(default))

    # need to get the result type before broadcasting for correct scalar
    # behaviour
    dtype = np.result_type(*choicelist)

    # Convert conditions to arrays and broadcast conditions and choices
    # as the shape is needed for the result. Doing it seperatly optimizes
    # for example when all choices are scalars.
    condlist = np.broadcast_arrays(*condlist)
    choicelist = np.broadcast_arrays(*choicelist)

    # If cond array is not an ndarray in boolean format or scalar bool, abort.
    deprecated_ints = False
    for i in range(len(condlist)):
        cond = condlist[i]
        if cond.dtype.type is not np.bool_:
            if np.issubdtype(cond.dtype, np.integer):
                # A previous implementation accepted int ndarrays accidentally.
                # Supported here deliberately, but deprecated.
                condlist[i] = condlist[i].astype(bool)
                deprecated_ints = True
            else:
                raise ValueError(
                    'invalid entry in choicelist: should be boolean ndarray')

    if deprecated_ints:
        msg = "select condlists containing integer ndarrays is deprecated " \
            "and will be removed in the future. Use `.astype(bool)` to " \
            "convert to bools."
        warnings.warn(msg, DeprecationWarning)

    if choicelist[0].ndim == 0:
        # This may be common, so avoid the call.
        result_shape = condlist[0].shape
    else:
        result_shape = np.broadcast_arrays(condlist[0], choicelist[0])[0].shape

    result = np.full(result_shape, choicelist[-1], dtype)

    # Use np.copyto to burn each choicelist array onto result, using the
    # corresponding condlist as a boolean mask. This is done in reverse
    # order since the first choice should take precedence.
    choicelist = choicelist[-2::-1]
    condlist = condlist[::-1]
    for choice, cond in zip(choicelist, condlist):
        np.copyto(result, choice, where=cond)

    return result