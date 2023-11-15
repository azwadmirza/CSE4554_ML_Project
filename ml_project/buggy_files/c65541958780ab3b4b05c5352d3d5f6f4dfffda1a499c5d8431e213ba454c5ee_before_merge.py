def get_loginclass(name):
    '''
    Get the login class of the user

    .. note::
        This function only applies to OpenBSD systems.

    CLI Example:

    .. code-block:: bash

        salt '*' user.get_loginclass foo
    '''
    if __grains__['kernel'] != 'OpenBSD':
        return False
    userinfo = __salt__['cmd.run_stdout'](
        ['userinfo', name],
        python_shell=False)
    for line in userinfo.splitlines():
        if line.startswith('class'):
            try:
                ret = line.split(None, 1)[1]
                break
            except ValueError:
                continue
    else:
        ret = ''
    return ret