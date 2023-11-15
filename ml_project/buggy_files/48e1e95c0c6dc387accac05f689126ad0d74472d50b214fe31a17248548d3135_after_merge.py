def get(zpool, prop=None, show_source=False, parsable=True):
    '''
    .. versionadded:: 2016.3.0

    Retrieves the given list of properties

    zpool : string
        Name of storage pool

    prop : string
        Optional name of property to retrieve

    show_source : boolean
        Show source of property

    parsable : boolean
        Display numbers in parsable (exact) values

        .. versionadded:: 2018.3.0

    CLI Example:

    .. code-block:: bash

        salt '*' zpool.get myzpool

    '''
    ret = OrderedDict()
    value_properties = ['property', 'value', 'source']

    ## collect get output
    res = __salt__['cmd.run_all'](
        __utils__['zfs.zpool_command'](
            command='get',
            flags=['-H'],
            opts={'-o': ','.join(value_properties)},
            property_name=prop if prop else 'all',
            target=zpool,
        ),
        python_shell=False,
    )

    if res['retcode'] != 0:
        return __utils__['zfs.parse_command_result'](res)

    # NOTE: command output for reference
    # ========================================================================
    # ...
    # data  mountpoint  /data   local
    # data  compression off     default
    # ...
    # =========================================================================

    # parse get output
    for line in res['stdout'].splitlines():
        # NOTE: transform data into dict
        prop_data = OrderedDict(list(zip(
            value_properties,
            [x for x in line.strip().split('\t') if x not in ['']],
        )))

        # NOTE: normalize values
        if parsable:
            # NOTE: raw numbers and pythonic types
            prop_data['value'] = __utils__['zfs.from_auto'](prop_data['property'], prop_data['value'])
        else:
            # NOTE: human readable zfs types
            prop_data['value'] = __utils__['zfs.to_auto'](prop_data['property'], prop_data['value'])

        # NOTE: show source if requested
        if show_source:
            ret[prop_data['property']] = prop_data
            del ret[prop_data['property']]['property']
        else:
            ret[prop_data['property']] = prop_data['value']

    return ret