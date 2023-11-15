def _run_svn(cmd, cwd, user, username, password, opts, **kwargs):
    '''
    Execute svn
    return the output of the command

    cmd
        The command to run.

    cwd
        The path to the Subversion repository

    user
        Run svn as a user other than what the minion runs as

    username
        Connect to the Subversion server as another user

    password
        Connect to the Subversion server with this password

        .. versionadded:: 0.17.0

    opts
        Any additional options to add to the command line

    kwargs
        Additional options to pass to the run-cmd
    '''
    cmd = ['svn', '--non-interactive', cmd]

    options = list(opts)
    if username:
        options.extend(['--username', username])
    if password:
        options.extend(['--password', password])
    cmd.extend(options)

    result = __salt__['cmd.run_all'](cmd, python_shell=False, cwd=cwd, runas=user, **kwargs)

    retcode = result['retcode']

    if retcode == 0:
        return result['stdout']
    raise exceptions.CommandExecutionError(result['stderr'] + '\n\n' + ' '.join(cmd))