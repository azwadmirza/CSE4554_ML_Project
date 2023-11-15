def add_source(name, source_location, username=None, password=None):
    '''
    Instructs Chocolatey to add a source.

    name
        The name of the source to be added as a chocolatey repository.

    source
        Location of the source you want to work with.

    username
        Provide username for chocolatey sources that need authentication
        credentials.

    password
        Provide password for chocolatey sources that need authentication
        credentials.

    CLI Example:

    .. code-block:: bash

        salt '*' chocolatey.add_source <source name> <source_location>
        salt '*' chocolatey.add_source <source name> <source_location> user=<user> password=<password>

    '''
    choc_path = _find_chocolatey(__context__, __salt__)
    cmd = [choc_path, 'sources', 'add', '--name', name, '--source', source_location]
    if username:
        cmd.extend(['--user', username])
    if password:
        cmd.extend(['--password', password])
    result = __salt__['cmd.run_all'](cmd, python_shell=False)

    if result['retcode'] != 0:
        err = 'Running chocolatey failed: {0}'.format(result['stdout'])
        raise CommandExecutionError(err)

    return result['stdout']