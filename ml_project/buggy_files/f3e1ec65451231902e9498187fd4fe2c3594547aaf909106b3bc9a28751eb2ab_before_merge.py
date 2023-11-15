def get(*dataset, **kwargs):
    '''
    Displays properties for the given datasets.

    *dataset : string
        name of snapshot(s), filesystem(s), or volume(s)
    properties : string
        comma-separated list of properties to list, defaults to all
    recursive : boolean
        recursively list children
    depth : int
        recursively list children to depth
    fields : string
        comma-separated list of fields to include, the name and property field will always be added
    type : string
        comma-separated list of types to display, where type is one of
        filesystem, snapshot, volume, bookmark, or all.
    source : string
        comma-separated list of sources to display. Must be one of the following:
        local, default, inherited, temporary, and none. The default value is all sources.
    parsable : boolean
        display numbers in parsable (exact) values (default = True)
        .. versionadded:: 2018.3.0

    .. note::

        If no datasets are specified, then the command displays properties
        for all datasets on the system.

    .. versionadded:: 2016.3.0

    CLI Example:

    .. code-block:: bash

        salt '*' zfs.get
        salt '*' zfs.get myzpool/mydataset [recursive=True|False]
        salt '*' zfs.get myzpool/mydataset properties="sharenfs,mountpoint" [recursive=True|False]
        salt '*' zfs.get myzpool/mydataset myzpool/myotherdataset properties=available fields=value depth=1

    '''
    ## Configure command
    # NOTE: initialize the defaults
    flags = ['-H', '-p']
    opts = {}

    # NOTE: set extra config from kwargs
    if kwargs.get('depth', False):
        opts['-d'] = kwargs.get('depth')
    elif kwargs.get('recursive', False):
        flags.append('-r')
    fields = kwargs.get('fields', 'value,source').split(',')
    if 'name' in fields:      # ensure name is first
        fields.remove('name')
    if 'property' in fields:  # ensure property is second
        fields.remove('property')
    fields.insert(0, 'name')
    fields.insert(1, 'property')
    opts['-o'] = ",".join(fields)
    if kwargs.get('type', False):
        opts['-t'] = kwargs.get('type')
    if kwargs.get('source', False):
        opts['-s'] = kwargs.get('source')

    # NOTE: set property_name
    property_name = kwargs.get('properties', 'all')

    ## Get properties
    res = __salt__['cmd.run_all'](
        __utils__['zfs.zfs_command'](
            command='get',
            flags=flags,
            opts=opts,
            property_name=property_name,
            target=list(dataset),
        ),
        python_shell=False,
    )

    ret = __utils__['zfs.parse_command_result'](res)
    if res['retcode'] == 0:
        for ds in res['stdout'].splitlines():
            ds_data = OrderedDict(list(zip(
                fields,
                ds.split("\t")
            )))

            if 'value' in ds_data:
                if kwargs.get('parsable', True):
                    ds_data['value'] = __utils__['zfs.from_auto'](
                        ds_data['property'],
                        ds_data['value'],
                    )
                else:
                    ds_data['value'] = __utils__['zfs.to_auto'](
                        ds_data['property'],
                        ds_data['value'],
                        convert_to_human=True,
                    )

            if ds_data['name'] not in ret:
                ret[ds_data['name']] = OrderedDict()

            ret[ds_data['name']][ds_data['property']] = ds_data
            del ds_data['name']
            del ds_data['property']

    return ret