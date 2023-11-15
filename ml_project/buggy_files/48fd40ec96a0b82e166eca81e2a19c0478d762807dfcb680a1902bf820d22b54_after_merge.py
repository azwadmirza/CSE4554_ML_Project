def uninstall(name, version=None, uninstall_args=None, override_args=False):
    '''
    Instructs Chocolatey to uninstall a package.

    name
        The name of the package to be uninstalled. Only accepts a single
        argument.

    version
        Uninstalls a specific version of the package. Defaults to latest version
        installed.

    uninstall_args
        A list of uninstall arguments you want to pass to the uninstallation
        process i.e product key or feature list

    override_args
        Set to true if you want to override the original uninstall arguments
        (for the native uninstaller) in the package and use your own. When this
        is set to False uninstall_args will be appended to the end of the
        default arguments

    CLI Example:

    .. code-block:: bash

        salt '*' chocolatey.uninstall <package name>
        salt '*' chocolatey.uninstall <package name> version=<package version>
        salt '*' chocolatey.uninstall <package name> version=<package version> uninstall_args=<args> override_args=True
    '''
    # chocolatey helpfully only supports a single package argument
    cmd = [_find_chocolatey(), 'uninstall', name]
    if version:
        cmd.extend(['--version', version])
    if uninstall_args:
        cmd.extend(['--uninstallarguments', uninstall_args])
    if override_args:
        cmd.extend(['--overridearguments'])
    cmd.extend(_yes())
    result = __salt__['cmd.run_all'](cmd, python_shell=False)

    if result['retcode'] not in [0, 1605, 1614, 1641]:
        err = 'Running chocolatey failed: {0}'.format(result['stdout'])
        raise CommandExecutionError(err)

    return result['stdout']