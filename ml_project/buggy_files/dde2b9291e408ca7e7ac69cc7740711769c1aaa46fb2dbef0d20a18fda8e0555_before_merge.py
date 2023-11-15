def set(*dataset, **kwargs):
    '''
    Sets the property or list of properties to the given value(s) for each dataset.

    dataset : string
        name of snapshot(s), filesystem(s), or volume(s)
    properties : string
        additional zfs properties pairs

    .. note::

        properties are passed as key-value pairs. e.g.

            compression=off

    .. note::

        Only some properties can be edited.

        See the Properties section for more information on what properties
        can be set and acceptable values.

        Numeric values can be specified as exact values, or in a human-readable
        form with a suffix of B, K, M, G, T, P, E (for bytes, kilobytes,
        megabytes, gigabytes, terabytes, petabytes, or exabytes respectively).

    .. versionadded:: 2016.3.0

    CLI Example:

    .. code-block:: bash

        salt '*' zfs.set myzpool/mydataset compression=off
        salt '*' zfs.set myzpool/mydataset myzpool/myotherdataset compression=off
        salt '*' zfs.set myzpool/mydataset myzpool/myotherdataset compression=lz4 canmount=off

    '''
    ## Configure command
    # NOTE: push filesystem properties
    filesystem_properties = salt.utils.args.clean_kwargs(**kwargs)

    ## Set property
    res = __salt__['cmd.run_all'](
        __utils__['zfs.zfs_command'](
            command='set',
            property_name=filesystem_properties.keys(),
            property_value=filesystem_properties.values(),
            target=list(dataset),
        ),
        python_shell=False,
    )

    return __utils__['zfs.parse_command_result'](res, 'set')