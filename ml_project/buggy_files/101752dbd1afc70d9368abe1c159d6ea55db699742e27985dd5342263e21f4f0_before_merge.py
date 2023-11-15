def ls(bank):
    '''
    Return an iterable object containing all entries stored in the specified
    bank.
    '''
    _init_client()
    path = '{0}/{1}'.format(path_prefix, bank)
    try:
        return _walk(client.get(path))
    except Exception as exc:
        raise SaltCacheError(
            'There was an error getting the key "{0}": {1}'.format(
                bank, exc
            )
        )