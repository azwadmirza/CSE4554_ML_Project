def _zfs_pool_data():
    '''
    Provide grains about zpools
    '''
    grains = {}

    # collect zpool data
    zpool_list_cmd = __utils__['zfs.zpool_command'](
        'list',
        flags=['-H', '-p'],
        opts={'-o': 'name,size'},
    )
    for zpool in __salt__['cmd.run'](zpool_list_cmd).splitlines():
        if 'zpool' not in grains:
            grains['zpool'] = {}
        zpool = zpool.split()
        grains['zpool'][zpool[0]] = __utils__['zfs.to_size'](zpool[1], True)

    # return grain data
    return grains