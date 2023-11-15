def get_async_pillar(opts, grains, id_, saltenv=None, ext=None, env=None, funcs=None,
               pillar=None, pillarenv=None):
    '''
    Return the correct pillar driver based on the file_client option
    '''
    if env is not None:
        salt.utils.warn_until(
            'Boron',
            'Passing a salt environment should be done using \'saltenv\' '
            'not \'env\'. This functionality will be removed in Salt Boron.'
        )
        # Backwards compatibility
        saltenv = env
    ptype = {
        'remote': AsyncRemotePillar,
        'local': AsyncPillar,
    }.get(opts['file_client'], AsyncPillar)
    return ptype(opts, grains, id_, saltenv, ext, functions=funcs,
                 pillar=pillar, pillarenv=pillarenv)