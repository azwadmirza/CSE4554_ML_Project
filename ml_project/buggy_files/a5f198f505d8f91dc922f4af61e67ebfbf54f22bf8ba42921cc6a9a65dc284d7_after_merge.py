def swapoff(name):
    '''
    Deactivate a named swap mount

    .. versionchanged:: 2016.3.2

    CLI Example:

    .. code-block:: bash

        salt '*' mount.swapoff /root/swapfile
    '''
    on_ = swaps()
    if name in on_:
        if __grains__['kernel'] == 'SunOS':
            if __grains__['virtual'] != 'zone':
                __salt__['cmd.run']('swap -a {0}'.format(name), python_shell=False)
            else:
                return False
        elif __grains__['os'] != 'OpenBSD':
            __salt__['cmd.run']('swapoff {0}'.format(name), python_shell=False)
        else:
            __salt__['cmd.run']('swapctl -d {0}'.format(name),
                                python_shell=False)
        on_ = swaps()
        if name in on_:
            return False
        return True
    return None