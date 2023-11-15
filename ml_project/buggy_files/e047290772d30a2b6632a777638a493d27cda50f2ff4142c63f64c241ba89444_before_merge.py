def chgid(name, gid, root=None):
    '''
    Change the default group of the user

    CLI Example:

    .. code-block:: bash

        salt '*' user.chgid foo 4376
    '''
    pre_info = info(name)
    if gid == pre_info['gid']:
        return True
    cmd = ['usermod', '-g', '{0}'.format(gid), name]

    if root is not None:
        cmd.extend(('-R', root))

    __salt__['cmd.run'](cmd, python_shell=False)
    return info(name).get('gid') == gid