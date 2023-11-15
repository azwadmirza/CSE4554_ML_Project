def swapoff(name):
    '''
    Deactivate a named swap mount

    CLI Example:

    .. code-block:: bash

        salt '*' mount.swapoff /root/swapfile
    '''
    on_ = swaps()
    if name in on_:
        if __grains__['os'] != 'OpenBSD':
            __salt__['cmd.run']('swapoff {0}'.format(name), python_shell=False)
        else:
            __salt__['cmd.run']('swapctl -d {0}'.format(name),
                                python_shell=False)
        on_ = swaps()
        if name in on_:
            return False
        return True
    return None