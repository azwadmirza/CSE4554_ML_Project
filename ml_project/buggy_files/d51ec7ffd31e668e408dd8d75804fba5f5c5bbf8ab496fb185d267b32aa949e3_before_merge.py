def normalize_known_hosts_key(key):
    '''
    Transform a key, either taken from a known_host file or provided by the
    user, into a normalized form.
    The host part (which might include multiple hostnames or be hashed) gets
    replaced by the provided host. Also, any spurious information gets removed
    from the end (like the username@host tag usually present in hostkeys, but
    absent in known_hosts files)
    '''
    k = key.strip()  # trim trailing newline
    k = key.split()
    d = dict()
    # The optional "marker" field, used for @cert-authority or @revoked
    if k[0][0] == '@':
        d['options'] = k[0]
        d['host'] = k[1]
        d['type'] = k[2]
        d['key'] = k[3]
    else:
        d['host'] = k[0]
        d['type'] = k[1]
        d['key'] = k[2]
    return d