def update(clear=False, mine_functions=None):
    '''
    Call the configured functions and send the data back up to the master.
    The functions to be called are merged from the master config, pillar and
    minion config under the option `mine_functions`:

    .. code-block:: yaml

        mine_functions:
          network.ip_addrs:
            - eth0
          disk.usage: []

    This function accepts the following arguments:

    :param bool clear: Default: ``False``
        Specifies whether updating will clear the existing values (``True``), or
        whether it will update them (``False``).

    :param dict mine_functions:
        Update (or clear, see ``clear``) the mine data on these functions only.
        This will need to have the structure as defined on
        https://docs.saltstack.com/en/latest/topics/mine/index.html#mine-functions

        This feature can be used when updating the mine for functions
        that require a refresh at different intervals than the rest of
        the functions specified under `mine_functions` in the
        minion/master config or pillar.
        A potential use would be together with the `scheduler`, for example:

        .. code-block:: yaml

            schedule:
              lldp_mine_update:
                function: mine.update
                kwargs:
                    mine_functions:
                      net.lldp: []
                hours: 12

        In the example above, the mine for `net.lldp` would be refreshed
        every 12 hours, while  `network.ip_addrs` would continue to be updated
        as specified in `mine_interval`.

    The function cache will be populated with information from executing these
    functions

    CLI Example:

    .. code-block:: bash

        salt '*' mine.update
    '''
    if not mine_functions:
        mine_functions = __salt__['config.merge']('mine_functions', {})
        # If we don't have any mine functions configured, then we should just bail out
        if not mine_functions:
            return
    elif isinstance(mine_functions, list):
        mine_functions = dict((fun, {}) for fun in mine_functions)
    elif isinstance(mine_functions, dict):
        pass
    else:
        return

    mine_data = {}
    for function_alias, function_data in six.iteritems(mine_functions):
        function_name, function_args, function_kwargs, minion_acl = \
            salt.utils.mine.parse_function_definition(function_data)
        if not _mine_function_available(function_name or function_alias):
            continue
        try:
            res = salt.utils.functools.call_function(
                __salt__[function_name or function_alias],
                *function_args,
                **function_kwargs
            )
        except Exception:  # pylint: disable=broad-except
            trace = traceback.format_exc()
            log.error('Function %s in mine.update failed to execute', function_name or function_alias)
            log.debug('Error: %s', trace)
            continue
        mine_data[function_alias] = salt.utils.mine.wrap_acl_structure(
            res,
            **minion_acl
        )
    return _mine_store(mine_data, clear)