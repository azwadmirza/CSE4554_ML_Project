def active(extended=False):
    '''
    List the active mounts.

    CLI Example:

    .. code-block:: bash

        salt '*' mount.active
    '''
    ret = {}
    if __grains__['os'] == 'FreeBSD':
        _active_mounts_freebsd(ret)
    elif __grains__['os'] == 'Solaris':
        _active_mounts_solaris(ret)
    elif __grains__['os'] == 'OpenBSD':
        _active_mounts_openbsd(ret)
    elif __grains__['os'] in ['MacOS', 'Darwin']:
        _active_mounts_darwin(ret)
    else:
        if extended:
            try:
                _active_mountinfo(ret)
            except CommandExecutionError:
                _active_mounts(ret)
        else:
            _active_mounts(ret)
    return ret