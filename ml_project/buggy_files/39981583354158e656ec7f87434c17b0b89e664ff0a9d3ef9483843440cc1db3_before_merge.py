def store(bank, key, data):
    '''
    Store a key value.
    '''
    _init_client()
    etcd_key = '{0}/{1}/{2}'.format(path_prefix, bank, key)
    try:
        value = __context__['serial'].dumps(data)
        client.set(etcd_key, value)
    except Exception as exc:
        raise SaltCacheError(
            'There was an error writing the key, {0}: {1}'.format(etcd_key, exc)
        )