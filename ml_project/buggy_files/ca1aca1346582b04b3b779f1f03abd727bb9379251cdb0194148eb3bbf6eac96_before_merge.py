def get_pillar(opts, grains, minion_id, saltenv=None, ext=None, funcs=None,
               pillar=None, pillarenv=None, rend=None):
    '''
    Return the correct pillar driver based on the file_client option
    '''
    ptype = {
        'remote': RemotePillar,
        'local': Pillar
    }.get(opts['file_client'], Pillar)
    # If local pillar and we're caching, run through the cache system first
    log.debug('Determining pillar cache')
    if opts['pillar_cache']:
        log.info('Compiling pillar from cache')
        log.debug('get_pillar using pillar cache with ext: {0}'.format(ext))
        return PillarCache(opts, grains, minion_id, saltenv, ext=ext, functions=funcs,
                pillar=pillar, pillarenv=pillarenv)
    return ptype(opts, grains, minion_id, saltenv, ext, functions=funcs,
                 pillar=pillar, pillarenv=pillarenv, rend=rend)