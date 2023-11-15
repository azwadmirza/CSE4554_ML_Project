def fetch(bank, key):
    '''
    Fetch a key value.
    '''
    _init_client()
    etcd_key = '{0}/{1}/{2}'.format(path_prefix, bank, key)
    try:
        value = client.get(etcd_key).value
        if value is None:
            return {}
        return __context__['serial'].loads(value)
    except Exception as exc:
        raise SaltCacheError(
            'There was an error reading the key, {0}: {1}'.format(
                etcd_key, exc
            )
        )