def get_loginclass(name):
    '''
    Get the login class of the user

    .. versionadded:: 2016.3.0

    CLI Example:

    .. code-block:: bash

        salt '*' user.get_loginclass foo

    '''

    userinfo = __salt__['cmd.run_stdout']('pw usershow -n {0}'.format(name))
    userinfo = userinfo.split(':')

    return {'loginclass': userinfo[4] if len(userinfo) == 10 else ''}