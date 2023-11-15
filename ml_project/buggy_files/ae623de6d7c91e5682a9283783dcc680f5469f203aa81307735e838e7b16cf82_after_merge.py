def flush(bank, key=None):
    '''
    Remove the key from the cache bank with all the key content.
    '''
    _init_client()
    if key is None:
        etcd_key = '{0}/{1}'.format(path_prefix, bank)
    else:
        etcd_key = '{0}/{1}/{2}'.format(path_prefix, bank, key)
    try:
        client.read(etcd_key)
    except etcd.EtcdKeyNotFound:
        return  # nothing to flush
    try:
        client.delete(etcd_key, recursive=True)
    except Exception as exc:
        raise SaltCacheError(
            'There was an error removing the key, {0}: {1}'.format(
                etcd_key, exc
            )
        )