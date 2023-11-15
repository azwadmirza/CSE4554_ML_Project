def launchctl(sub_cmd, *args, **kwargs):
    '''
    Run a launchctl command and raise an error if it fails

    Args: additional args are passed to launchctl
        sub_cmd (str): Sub command supplied to launchctl

    Kwargs: passed to ``cmd.run_all``
        return_stdout (bool): A keyword argument. If true return the stdout of
            the launchctl command

    Returns:
        bool: ``True`` if successful
        str: The stdout of the launchctl command if requested

    Raises:
        CommandExecutionError: If command fails

    CLI Example:

    .. code-block:: bash

        import salt.utils.mac_service
        salt.utils.mac_service.launchctl('debug', 'org.cups.cupsd')
    '''
    # Get return type
    return_stdout = kwargs.pop('return_stdout', False)

    # Construct command
    cmd = ['launchctl', sub_cmd]
    cmd.extend(args)

    # Run command
    kwargs['python_shell'] = False
    kwargs = salt.utils.args.clean_kwargs(**kwargs)
    ret = __salt__['cmd.run_all'](cmd, **kwargs)

    # Raise an error or return successful result
    if ret['retcode']:
        out = 'Failed to {0} service:\n'.format(sub_cmd)
        out += 'stdout: {0}\n'.format(ret['stdout'])
        out += 'stderr: {0}\n'.format(ret['stderr'])
        out += 'retcode: {0}'.format(ret['retcode'])
        raise CommandExecutionError(out)
    else:
        return ret['stdout'] if return_stdout else True