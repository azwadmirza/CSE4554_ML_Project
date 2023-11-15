def fetch(bank, key):
    '''
    Fetch a key value.
    '''
    _init_client()
    etcd_key = '{0}/{1}/{2}'.format(path_prefix, bank, key)
    try:
        value = client.read(etcd_key).value
        return __context__['serial'].loads(base64.b64decode(value))
    except etcd.EtcdKeyNotFound:
        return {}
    except Exception as exc:
        raise SaltCacheError(
            'There was an error reading the key, {0}: {1}'.format(
                etcd_key, exc
            )
        )