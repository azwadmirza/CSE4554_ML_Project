def list_windowsfeatures():
    '''
    Instructs Chocolatey to pull a full package list from the Windows Features
    list, via the Deployment Image Servicing and Management tool.

    Returns:
        str: List of Windows Features

    CLI Example:

    .. code-block:: bash

        salt '*' chocolatey.list_windowsfeatures
    '''
    choc_path = _find_chocolatey()
    cmd = [choc_path, 'list', '--source', 'windowsfeatures']
    result = __salt__['cmd.run_all'](cmd, python_shell=False)

    if result['retcode'] != 0:
        err = 'Running chocolatey failed: {0}'.format(result['stdout'])
        raise CommandExecutionError(err)

    return result['stdout']