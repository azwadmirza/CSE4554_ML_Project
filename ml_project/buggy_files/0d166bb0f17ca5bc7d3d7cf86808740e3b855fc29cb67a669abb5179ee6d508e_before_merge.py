def change_minion_cachedir(
        minion_id,
        cachedir,
        data=None,
        base=None,
):
    '''
    Changes the info inside a minion's cachedir entry. The type of cachedir
    must be specified (i.e., 'requested' or 'active'). A dict is also passed in
    which contains the data to be changed.

    Example:

        change_minion_cachedir(
            'myminion',
            'requested',
            {'fingerprint': '26:5c:8c:de:be:fe:89:c0:02:ed:27:65:0e:bb:be:60'},
        )
    '''
    if not isinstance(data, dict):
        return False

    if base is None:
        base = __opts__['cachedir']

    fname = '{0}.p'.format(minion_id)
    path = os.path.join(base, cachedir, fname)

    with salt.utils.fopen(path, 'r') as fh_:
        cache_data = msgpack.load(fh_)

    cache_data.update(data)

    with salt.utils.fopen(path, 'w') as fh_:
        msgpack.dump(cache_data, fh_)