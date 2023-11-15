def chshell(name, shell, root=None):
    '''
    Change the default shell of the user

    CLI Example:

    .. code-block:: bash

        salt '*' user.chshell foo /bin/zsh
    '''
    pre_info = info(name)
    if shell == pre_info['shell']:
        return True
    cmd = ['usermod', '-s', shell, name]

    if root is not None:
        cmd.extend(('-R', root))

    __salt__['cmd.run'](cmd, python_shell=False)
    return info(name).get('shell') == shell