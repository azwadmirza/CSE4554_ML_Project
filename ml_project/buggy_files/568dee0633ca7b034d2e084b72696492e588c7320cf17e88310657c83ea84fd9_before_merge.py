def contains(bank, key):
    '''
    Checks if the specified bank contains the specified key.
    '''
    _init_client()
    etcd_key = '{0}/{1}/{2}'.format(path_prefix, bank, key)
    try:
        r = client.get(etcd_key)
        # return True for keys, not dirs
        return r.dir is False
    except etcd.EtcdKeyNotFound:
        return False
    except Exception as exc:
        raise SaltCacheError(
            'There was an error getting the key, {0}: {1}'.format(
                etcd_key, exc
            )
        )