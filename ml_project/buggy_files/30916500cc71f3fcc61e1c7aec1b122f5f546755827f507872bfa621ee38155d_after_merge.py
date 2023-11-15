def chocolatey_version():
    '''
    Returns the version of Chocolatey installed on the minion.

    CLI Example:

    .. code-block:: bash

        salt '*' chocolatey.chocolatey_version
    '''
    if 'chocolatey._version' in __context__:
        return __context__['chocolatey._version']

    cmd = [_find_chocolatey()]
    cmd.append('-v')
    out = __salt__['cmd.run'](cmd, python_shell=False)
    __context__['chocolatey._version'] = out

    return __context__['chocolatey._version']