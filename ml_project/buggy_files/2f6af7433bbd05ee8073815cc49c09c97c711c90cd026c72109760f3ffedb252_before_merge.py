def send(name, *args, **kwargs):
    '''
    Send a specific function and its result to the salt mine.
    This gets stored in either the local cache, or the salt master's cache.

    :param str name: Name of the function to add to the mine.

    The following pameters are extracted from kwargs if present:

    :param str mine_function: The name of the execution_module.function to run
        and whose value will be stored in the salt mine. Defaults to ``name``.
    :param str allow_tgt: Targeting specification for ACL. Specifies which minions
        are allowed to access this function.
    :param str allow_tgt_type: Type of the targeting specification. This value will
        be ignored if ``allow_tgt`` is not specified.

    Remaining args and kwargs will be passed on to the function to run.

    :rtype: bool
    :return: Whether executing the function and storing the information was succesful.

    .. versionchanged:: 3000

        Added ``allow_tgt``- and ``allow_tgt_type``-parameters to specify which
        minions are allowed to access this function.
        See :ref:`targeting` for more information about targeting.

    CLI Example:

    .. code-block:: bash

        salt '*' mine.send network.ip_addrs eth0
        salt '*' mine.send eth0_ip_addrs mine_function=network.ip_addrs eth0
        salt '*' mine.send eth0_ip_addrs mine_function=network.ip_addrs eth0 allow_tgt='G@grain:value' allow_tgt_type=compound
    '''
    kwargs = salt.utils.args.clean_kwargs(**kwargs)
    mine_function = kwargs.pop('mine_function', None)
    allow_tgt = kwargs.pop('allow_tgt', None)
    allow_tgt_type = kwargs.pop('allow_tgt_type', None)
    mine_data = {}
    try:
        res = salt.utils.functools.call_function(
            __salt__[mine_function or name],
            *args,
            **kwargs
        )
    except Exception as exc:  # pylint: disable=broad-except
        trace = traceback.format_exc()
        log.error('Function %s in mine.send failed to execute', mine_function or name)
        log.debug('Error: %s', trace)
        return False
    mine_data[name] = salt.utils.mine.wrap_acl_structure(
        res,
        allow_tgt=allow_tgt,
        allow_tgt_type=allow_tgt_type
    )
    return _mine_store(mine_data)