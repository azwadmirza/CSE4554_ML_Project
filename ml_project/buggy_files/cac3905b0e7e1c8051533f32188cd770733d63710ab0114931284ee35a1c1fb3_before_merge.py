def _walk(r):
    '''
    Recursively walk dirs. Return flattened list of keys.
    r: etcd.EtcdResult
    '''
    if not r.dir:
        return [r.key.split('/', 3)[3]]

    keys = []
    for c in client.get(r.key).children:
        keys.extend(_walk(c))
    return keys