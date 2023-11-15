def swapon(name, priority=None):
    '''
    Activate a swap disk

    CLI Example:

    .. code-block:: bash

        salt '*' mount.swapon /root/swapfile
    '''
    ret = {}
    on_ = swaps()
    if name in on_:
        ret['stats'] = on_[name]
        ret['new'] = False
        return ret
    cmd = 'swapon {0}'.format(name)
    if priority:
        cmd += ' -p {0}'.format(priority)
    __salt__['cmd.run'](cmd, python_shell=False)
    on_ = swaps()
    if name in on_:
        ret['stats'] = on_[name]
        ret['new'] = True
        return ret
    return ret