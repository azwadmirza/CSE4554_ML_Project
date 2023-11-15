def _load_cached_grains(opts, cfn):
    '''
    Returns the grains cached in cfn, or None if the cache is too old or is
    corrupted.
    '''
    if not os.path.isfile(cfn):
        log.debug('Grains cache file does not exist.')
        return None

    grains_cache_age = int(time.time() - os.path.getmtime(cfn))
    if grains_cache_age > opts.get('grains_cache_expiration', 300):
        log.debug(
            'Grains cache last modified %s seconds ago and cache '
            'expiration is set to %s. Grains cache expired. '
            'Refreshing.',
            grains_cache_age, opts.get('grains_cache_expiration', 300)
        )
        return None

    if opts.get('refresh_grains_cache', False):
        log.debug('refresh_grains_cache requested, Refreshing.')
        return None

    log.debug('Retrieving grains from cache')
    try:
        serial = salt.payload.Serial(opts)
        with salt.utils.files.fopen(cfn, 'rb') as fp_:
            cached_grains = salt.utils.data.decode(serial.load(fp_), preserve_tuples=True)
        if not cached_grains:
            log.debug('Cached grains are empty, cache might be corrupted. Refreshing.')
            return None

        return cached_grains
    except (IOError, OSError):
        return None