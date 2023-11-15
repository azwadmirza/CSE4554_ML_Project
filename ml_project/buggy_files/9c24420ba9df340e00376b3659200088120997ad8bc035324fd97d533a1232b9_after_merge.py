def list_(properties='size,alloc,free,cap,frag,health', zpool=None, parsable=True):
    '''
    .. versionadded:: 2015.5.0

    Return information about (all) storage pools

    zpool : string
        optional name of storage pool

    properties : string
        comma-separated list of properties to list

    parsable : boolean
        display numbers in parsable (exact) values

        .. versionadded:: 2018.3.0

    .. note::

        The ``name`` property will always be included, while the ``frag``
        property will get removed if not available

    zpool : string
        optional zpool

    .. note::

        Multiple storage pool can be provded as a space separated list

    CLI Example:

    .. code-block:: bash

        salt '*' zpool.list
        salt '*' zpool.list zpool=tank
        salt '*' zpool.list 'size,free'
        salt '*' zpool.list 'size,free' tank

    '''
    ret = OrderedDict()

    ## update properties
    # NOTE: properties should be a list
    if not isinstance(properties, list):
        properties = properties.split(',')

    # NOTE: name should be first property
    while 'name' in properties:
        properties.remove('name')
    properties.insert(0, 'name')

    # NOTE: remove 'frags' if we don't have feature flags
    if not __utils__['zfs.has_feature_flags']():
        while 'frag' in properties:
            properties.remove('frag')

    ## collect list output
    res = __salt__['cmd.run_all'](
        __utils__['zfs.zpool_command'](
            command='list',
            flags=['-H'],
            opts={'-o': ','.join(properties)},
            target=zpool
        ),
        python_shell=False,
    )

    if res['retcode'] != 0:
        return __utils__['zfs.parse_command_result'](res)

    # NOTE: command output for reference
    # ========================================================================
    # data  1992864825344   695955501056    1296909324288   34  11%     ONLINE
    # =========================================================================

    ## parse list output
    for line in res['stdout'].splitlines():
        # NOTE: transform data into dict
        zpool_data = OrderedDict(list(zip(
            properties,
            line.strip().split('\t'),
        )))

        # NOTE: normalize values
        if parsable:
            # NOTE: raw numbers and pythonic types
            zpool_data = __utils__['zfs.from_auto_dict'](zpool_data)
        else:
            # NOTE: human readable zfs types
            zpool_data = __utils__['zfs.to_auto_dict'](zpool_data)

        ret[zpool_data['name']] = zpool_data
        del ret[zpool_data['name']]['name']

    return ret