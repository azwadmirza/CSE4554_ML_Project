def standardize_lag_order(order, title=None):
    """
    Standardize lag order input.

    Parameters
    ----------
    order : int or array_like
        Maximum lag order (if integer) or iterable of specific lag orders.
    title : str, optional
        Description of the order (e.g. "autoregressive") to use in error
        messages.

    Returns
    -------
    order : int or list of int
        Maximum lag order if consecutive lag orders were specified, otherwise
        a list of integer lag orders.

    Notes
    -----
    It is ambiguous if order=[1] is meant to be a boolean list or
    a list of lag orders to include, but this is irrelevant because either
    interpretation gives the same result.

    Order=[0] would be ambiguous, except that 0 is not a valid lag
    order to include, so there is no harm in interpreting as a boolean
    list, in which case it is the same as order=0, which seems like
    reasonable behavior.

    Examples
    --------
    >>> standardize_lag_order(3)
    3
    >>> standardize_lag_order(np.arange(1, 4))
    3
    >>> standardize_lag_order([1, 3])
    [1, 3]

    """
    order = np.array(order)
    title = 'order' if title is None else '%s order' % title

    # Only integer orders are valid
    if not np.all(order == order.astype(int)):
        raise ValueError('Invalid %s. Non-integer order (%s) given.'
                         % (title, order))
    order = order.astype(int)

    # Only positive integers are valid
    if np.any(order < 0):
        raise ValueError('Terms in the %s cannot be negative.')

    # Try to squeeze out an irrelevant trailing dimension
    if order.ndim == 2 and order.shape[1] == 1:
        order = order[:, 0]
    elif order.ndim > 1:
        raise ValueError('Invalid %s. Must be an integer or'
                         ' 1-dimensional array-like object (e.g. list,'
                         ' ndarray, etc.). Got %s.' % (title, order))

    # Option 1: the typical integer response (implies including all
    # lags up through and including the value)
    if order.ndim == 0:
        order = order.item()
    elif len(order) == 0:
        order = 0
    else:
        # Option 2: boolean list
        if 0 in order or np.sum(order == 1) > 1 and not np.any(order > 1):
            order = (np.where(order == 1)[0] + 1)

        # (Default) Option 3: list of lag orders to include
        else:
            order = np.sort(order)

        # If we have an empty list, set order to zero
        if len(order) == 0:
            order = 0
        # If we actually were given consecutive lag orders, just use integer
        elif np.all(order == np.arange(1, len(order) + 1)):
            order = order[-1]
        # Otherwise, convert to list
        else:
            order = order.tolist()

    return order