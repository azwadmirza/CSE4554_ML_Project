def upgrade(name,
            version=None,
            source=None,
            force=False,
            pre_versions=False,
            install_args=None,
            override_args=False,
            force_x86=False,
            package_args=None):
    '''
    .. versionadded:: 2016.3.4

    Instructs Chocolatey to upgrade packages on the system. (update is being
    deprecated)

    Args:

        name (str):
            The name of the package to update, or "all" to update everything
            installed on the system.

        version (str):
            Install a specific version of the package. Defaults to latest
            version.

        source (str):
            Chocolatey repository (directory, share or remote URL feed) the
            package comes from. Defaults to the official Chocolatey feed.

        force (bool):
            Reinstall the **same** version already installed

        pre_versions (bool):
            Include pre-release packages in comparison. Defaults to False.

        install_args (str):
            A list of install arguments you want to pass to the installation
            process i.e product key or feature list

        override_args (str):
            Set to true if you want to override the original install arguments
            (for the native installer) in the package and use your own. When
            this is set to False install_args will be appended to the end of the
            default arguments

        force_x86
            Force x86 (32bit) installation on 64 bit systems. Defaults to false.

        package_args
            A list of arguments you want to pass to the package

    Returns:
        str: Results of the ``chocolatey`` command

    CLI Example:

    .. code-block:: bash

        salt "*" chocolatey.upgrade all
        salt "*" chocolatey.upgrade <package name> pre_versions=True
    '''
    # chocolatey helpfully only supports a single package argument
    choc_path = _find_chocolatey(__context__, __salt__)
    cmd = [choc_path, 'upgrade', name]
    if version:
        cmd.extend(['-version', version])
    if source:
        cmd.extend(['--source', source])
    if salt.utils.is_true(force):
        cmd.append('--force')
    if salt.utils.is_true(pre_versions):
        cmd.append('--prerelease')
    if install_args:
        cmd.extend(['--installarguments', install_args])
    if override_args:
        cmd.append('--overridearguments')
    if force_x86:
        cmd.append('--forcex86')
    if package_args:
        cmd.extend(['--packageparameters', package_args])
    cmd.extend(_yes(__context__))

    result = __salt__['cmd.run_all'](cmd, python_shell=False)

    if result['retcode'] not in [0, 1641, 3010]:
        err = 'Running chocolatey failed: {0}'.format(result['stdout'])
        raise CommandExecutionError(err)

    return result['stdout']