def list_(name=None, **kwargs):
    '''
    Return a list of all datasets or a specified dataset on the system and the
    values of their used, available, referenced, and mountpoint properties.

    name : string
        name of dataset, volume, or snapshot
    recursive : boolean
        recursively list children
    depth : int
        limit recursion to depth
    properties : string
        comma-separated list of properties to list, the name property will always be added
    type : string
        comma-separated list of types to display, where type is one of
        filesystem, snapshot, volume, bookmark, or all.
    sort : string
        property to sort on (default = name)
    order : string [ascending|descending]
        sort order (default = ascending)
    parsable : boolean
        display numbers in parsable (exact) values
        .. versionadded:: 2018.3.0

    .. versionadded:: 2015.5.0

    CLI Example:

    .. code-block:: bash

        salt '*' zfs.list
        salt '*' zfs.list myzpool/mydataset [recursive=True|False]
        salt '*' zfs.list myzpool/mydataset properties="sharenfs,mountpoint"

    '''
    ret = OrderedDict()

    ## update properties
    # NOTE: properties should be a list
    properties = kwargs.get('properties', 'used,avail,refer,mountpoint')
    if not isinstance(properties, list):
        properties = properties.split(',')

    # NOTE: name should be first property
    #       we loop here because there 'name' can be in the list
    #       multiple times.
    while 'name' in properties:
        properties.remove('name')
    properties.insert(0, 'name')

    ## Configure command
    # NOTE: initialize the defaults
    flags = ['-H']
    opts = {}

    # NOTE: set extra config from kwargs
    if kwargs.get('recursive', False):
        flags.append('-r')
    if kwargs.get('recursive', False) and kwargs.get('depth', False):
        opts['-d'] = kwargs.get('depth')
    if kwargs.get('type', False):
        opts['-t'] = kwargs.get('type')
    kwargs_sort = kwargs.get('sort', False)
    if kwargs_sort and kwargs_sort in properties:
        if kwargs.get('order', 'ascending').startswith('a'):
            opts['-s'] = kwargs_sort
        else:
            opts['-S'] = kwargs_sort
    if isinstance(properties, list):
        # NOTE: There can be only one -o and it takes a comma-seperated list
        opts['-o'] = ','.join(properties)
    else:
        opts['-o'] = properties

    ## parse zfs list
    res = __salt__['cmd.run_all'](
        __utils__['zfs.zfs_command'](
            command='list',
            flags=flags,
            opts=opts,
            target=name,
        ),
        python_shell=False,
    )
    if res['retcode'] == 0:
        for ds in res['stdout'].splitlines():
            if kwargs.get('parsable', True):
                ds_data = __utils__['zfs.from_auto_dict'](
                    OrderedDict(list(zip(properties, ds.split("\t")))),
                )
            else:
                ds_data = __utils__['zfs.to_auto_dict'](
                    OrderedDict(list(zip(properties, ds.split("\t")))),
                    convert_to_human=True,
                )

            ret[ds_data['name']] = ds_data
            del ret[ds_data['name']]['name']
    else:
        return __utils__['zfs.parse_command_result'](res)

    return ret