def chhome(name, home, persist=False, root=None):
    '''
    Change the home directory of the user, pass True for persist to move files
    to the new home directory if the old home directory exist.

    CLI Example:

    .. code-block:: bash

        salt '*' user.chhome foo /home/users/foo True
    '''
    pre_info = info(name)
    if home == pre_info['home']:
        return True
    cmd = ['usermod', '-d', '{0}'.format(home)]

    if root is not None and __grains__['kernel'] != 'AIX':
        cmd.extend(('-R', root))

    if persist and __grains__['kernel'] != 'OpenBSD':
        cmd.append('-m')
    cmd.append(name)
    __salt__['cmd.run'](cmd, python_shell=False)
    return info(name).get('home') == home