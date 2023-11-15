def request_minion_cachedir(
        minion_id,
        opts=None,
        fingerprint='',
        pubkey=None,
        provider=None,
        base=None,
):
    '''
    Creates an entry in the requested/ cachedir. This means that Salt Cloud has
    made a request to a cloud provider to create an instance, but it has not
    yet verified that the instance properly exists.

    If the fingerprint is unknown, a raw pubkey can be passed in, and a
    fingerprint will be calculated. If both are empty, then the fingerprint
    will be set to None.
    '''
    if base is None:
        base = __opts__['cachedir']

    if not fingerprint and pubkey is not None:
        fingerprint = salt.utils.crypt.pem_finger(key=pubkey, sum_type=(opts and opts.get('hash_type') or 'sha256'))

    init_cachedir(base)

    data = {
        'minion_id': minion_id,
        'fingerprint': fingerprint,
        'provider': provider,
    }

    fname = '{0}.p'.format(minion_id)
    path = os.path.join(base, 'requested', fname)
    with salt.utils.files.fopen(path, 'w') as fh_:
        msgpack.dump(data, fh_)