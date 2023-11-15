def list_webpi():
    '''
    Instructs Chocolatey to pull a full package list from the Microsoft Web PI
    repository.

    Returns:
        str: List of webpi packages

    CLI Example:

    .. code-block:: bash

        salt '*' chocolatey.list_webpi
    '''
    choc_path = _find_chocolatey()
    cmd = [choc_path, 'list', '--source', 'webpi']
    result = __salt__['cmd.run_all'](cmd, python_shell=False)

    if result['retcode'] != 0:
        err = 'Running chocolatey failed: {0}'.format(result['stdout'])
        raise CommandExecutionError(err)

    return result['stdout']