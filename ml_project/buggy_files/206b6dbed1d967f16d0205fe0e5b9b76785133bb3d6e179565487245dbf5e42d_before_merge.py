def swaps():
    '''
    Return a dict containing information on active swap

    CLI Example:

    .. code-block:: bash

        salt '*' mount.swaps
    '''
    ret = {}
    if __grains__['os'] != 'OpenBSD':
        with salt.utils.fopen('/proc/swaps') as fp_:
            for line in fp_:
                if line.startswith('Filename'):
                    continue
                comps = line.split()
                ret[comps[0]] = {'type': comps[1],
                                 'size': comps[2],
                                 'used': comps[3],
                                 'priority': comps[4]}
    else:
        for line in __salt__['cmd.run_stdout']('swapctl -kl').splitlines():
            if line.startswith(('Device', 'Total')):
                continue
            swap_type = "file"
            comps = line.split()
            if comps[0].startswith('/dev/'):
                swap_type = "partition"
            ret[comps[0]] = {'type': swap_type,
                             'size': comps[1],
                             'used': comps[2],
                             'priority': comps[5]}
    return ret