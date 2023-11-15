def avail_sizes(conn=None, call=None):
    '''
    Return a dict of all available VM images on the cloud provider with
    relevant data
    '''
    if call == 'action':
        raise SaltCloudSystemExit(
            'The avail_sizes function must be called with '
            '-f or --function, or with the --list-sizes option'
        )

    if not conn:
        conn = get_conn()   # pylint: disable=E0602

    sizes = conn.list_sizes()
    ret = {}
    for size in sizes:
        if isinstance(size.name, string_types) and not six.PY3:
            size_name = size.name.encode('ascii', 'salt-cloud-force-ascii')
        else:
            size_name = str(size.name)

        ret[size_name] = {}
        for attr in dir(size):
            if attr.startswith('_'):
                continue

            try:
                attr_value = getattr(size, attr)
            except Exception:
                pass

            if isinstance(attr_value, string_types) and not six.PY3:
                attr_value = attr_value.encode(
                    'ascii', 'salt-cloud-force-ascii'
                )
            ret[size_name][attr] = attr_value
    return ret