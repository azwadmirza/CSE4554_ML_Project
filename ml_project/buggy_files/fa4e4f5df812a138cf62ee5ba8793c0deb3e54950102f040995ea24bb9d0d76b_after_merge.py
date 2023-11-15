def optional_args(proxy=None):
    '''
    Return the connection optional args.

    .. note::

        Sensible data will not be returned.

    .. versionadded:: 2017.7.0

    CLI Example - select all devices connecting via port 1234:

    .. code-block:: bash

        salt -G 'optional_args:port:1234' test.ping

    Output:

    .. code-block:: yaml

        device1:
            True
        device2:
            True
    '''
    opt_args = _get_device_grain('optional_args', proxy=proxy) or {}
    if opt_args and _FORBIDDEN_OPT_ARGS:
        for arg in _FORBIDDEN_OPT_ARGS:
            opt_args.pop(arg, None)
    return {'optional_args': opt_args}