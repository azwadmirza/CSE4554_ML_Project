def _user_mdata(mdata_list=None, mdata_get=None):
    '''
    User Metadata
    '''
    grains = {}

    if not mdata_list:
        mdata_list = salt.utils.path.which('mdata-list')

    if not mdata_get:
        mdata_get = salt.utils.path.which('mdata-get')

    if not mdata_list or not mdata_get:
        return grains

    for mdata_grain in __salt__['cmd.run'](mdata_list, ignore_retcode=True).splitlines():
        mdata_value = __salt__['cmd.run']('{0} {1}'.format(mdata_get, mdata_grain), ignore_retcode=True)

        if not mdata_grain.startswith('sdc:'):
            if 'mdata' not in grains:
                grains['mdata'] = {}

            log.debug('found mdata entry %s with value %s', mdata_grain, mdata_value)
            mdata_grain = mdata_grain.replace('-', '_')
            mdata_grain = mdata_grain.replace(':', '_')
            grains['mdata'][mdata_grain] = mdata_value

    return grains