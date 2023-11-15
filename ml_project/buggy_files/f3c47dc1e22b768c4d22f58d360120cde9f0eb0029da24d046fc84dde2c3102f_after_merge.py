def cache_nodes_ip(opts, base=None):
    '''
    Retrieve a list of all nodes from Salt Cloud cache, and any associated IP
    addresses. Returns a dict.
    '''
    salt.utils.versions.warn_until(
        'Fluorine',
        'This function is incomplete and non-functional '
        'and will be removed in Salt Fluorine.'
    )
    if base is None:
        base = opts['cachedir']

    minions = list_cache_nodes_full(opts, base=base)