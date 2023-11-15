def rename(name, new_name, root=None):
    '''
    Change the username for a named user

    CLI Example:

    .. code-block:: bash

        salt '*' user.rename name new_name
    '''
    current_info = info(name)
    if not current_info:
        raise CommandExecutionError('User \'{0}\' does not exist'.format(name))

    new_info = info(new_name)
    if new_info:
        raise CommandExecutionError(
            'User \'{0}\' already exists'.format(new_name)
        )

    cmd = ['usermod', '-l', '{0}'.format(new_name), '{0}'.format(name)]

    if root is not None and __grains__['kernel'] != 'AIX':
        cmd.extend(('-R', root))

    __salt__['cmd.run'](cmd, python_shell=False)
    return info(name).get('name') == new_name