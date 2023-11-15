def _zfs_support():
    '''
    Provide information about zfs kernel module
    '''
    grains = {'zfs_support': False}

    # Check for zfs support
    # NOTE: ZFS on Windows is in development
    # NOTE: ZFS on NetBSD is in development
    on_supported_platform = False
    if salt.utils.platform.is_sunos() and salt.utils.path.which('zfs'):
        on_supported_platform = True
    elif salt.utils.platform.is_freebsd() and _check_retcode('kldstat -q -m zfs'):
        on_supported_platform = True
    elif salt.utils.platform.is_linux():
        modinfo = salt.utils.path.which('modinfo')
        if modinfo:
            on_supported_platform = _check_retcode('{0} zfs'.format(modinfo))
        else:
            on_supported_platform = _check_retcode('ls /sys/module/zfs')

        # NOTE: fallback to zfs-fuse if needed
        if not on_supported_platform:
            _zfs_fuse = lambda f: __salt__['service.' + f]('zfs-fuse')
            if _zfs_fuse('available') and (_zfs_fuse('status') or _zfs_fuse('start')):
                on_supported_platform = True

    # Additional check for the zpool command
    if on_supported_platform and salt.utils.path.which('zpool'):
        grains['zfs_support'] = True

    return grains