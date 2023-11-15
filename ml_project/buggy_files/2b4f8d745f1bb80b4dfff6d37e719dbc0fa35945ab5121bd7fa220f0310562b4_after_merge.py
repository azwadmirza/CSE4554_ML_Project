def _get_source_sum(source_hash, file_path, saltenv):
    '''
    Extract the hash sum, whether it is in a remote hash file, or just a string.
    '''
    ret = dict()
    schemes = ('salt', 'http', 'https', 'ftp', 'swift', 's3', 'file')
    invalid_hash_msg = ("Source hash '{0}' format is invalid. It must be in "
                        "the format <hash type>=<hash>").format(source_hash)
    source_hash = str(source_hash)
    source_hash_scheme = _urlparse(source_hash).scheme

    if source_hash_scheme in schemes:
        # The source_hash is a file on a server
        cached_hash_file = __salt__['cp.cache_file'](source_hash, saltenv)

        if not cached_hash_file:
            raise CommandExecutionError(('Source hash file {0} not'
                                         ' found').format(source_hash))

        ret = __salt__['file.extract_hash'](cached_hash_file, '', file_path)
        if ret is None:
            raise SaltInvocationError(invalid_hash_msg)
    else:
        # The source_hash is a hash string
        items = source_hash.split('=', 1)

        if len(items) != 2:
            invalid_hash_msg = ('{0}, or it must be a supported protocol'
                                ': {1}').format(invalid_hash_msg,
                                                ', '.join(schemes))
            raise SaltInvocationError(invalid_hash_msg)

        ret['hash_type'], ret['hsum'] = [item.strip().lower() for item in items]

    return ret