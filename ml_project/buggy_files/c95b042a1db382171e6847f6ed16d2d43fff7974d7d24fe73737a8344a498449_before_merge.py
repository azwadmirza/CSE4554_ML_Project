def install(name,
            version=None,
            source=None,
            force=False,
            pre_versions=False,
            install_args=None,
            override_args=False,
            force_x86=False,
            package_args=None,
            allow_multiple=False):
    '''
    Instructs Chocolatey to install a package.

    Args:

        name (str):
            The name of the package to be installed. Only accepts a single
            argument. Required.

        version (str):
            Install a specific version of the package. Defaults to latest
            version. Default is None.

        source (str):
            Chocolatey repository (directory, share or remote URL feed) the
            package comes from. Defaults to the official Chocolatey feed.
            Default is None.

            Alternate Sources:

            - cygwin
            - python
            - ruby
            - webpi
            - windowsfeatures

        force (bool):
            Reinstall the current version of an existing package. Do not use
            with ``allow_multiple``. Default is False.

        pre_versions (bool):
            Include pre-release packages. Default is False.

        install_args (str):
            A list of install arguments you want to pass to the installation
            process i.e product key or feature list. Default is None.

        override_args (bool):
            Set to true if you want to override the original install arguments
            (for the native installer) in the package and use your own. When
            this is set to False install_args will be appended to the end of the
            default arguments. Default is None.

        force_x86 (bool):
            Force x86 (32bit) installation on 64 bit systems. Default is False.

        package_args (str):
            Arguments you want to pass to the package. Default is None.

        allow_multiple (bool):
            Allow multiple versions of the package to be installed. Do not use
            with ``force``. Does not work with all packages. Default is False.

            .. versionadded:: 2017.7.0

    Returns:
        str: The output of the ``chocolatey`` command

    CLI Example:

    .. code-block:: bash

        salt '*' chocolatey.install <package name>
        salt '*' chocolatey.install <package name> version=<package version>
        salt '*' chocolatey.install <package name> install_args=<args> override_args=True
    '''
    if force and allow_multiple:
        raise SaltInvocationError(
            'Cannot use \'force\' in conjunction with \'allow_multiple\'')

    choc_path = _find_chocolatey(__context__, __salt__)
    # chocolatey helpfully only supports a single package argument
    # CORRECTION: it also supports multiple package names separated by spaces
    # but any additional arguments apply to ALL packages specified
    cmd = [choc_path, 'install', name]
    if version:
        cmd.extend(['--version', version])
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
    if allow_multiple:
        cmd.append('--allow-multiple')
    cmd.extend(_yes(__context__))
    result = __salt__['cmd.run_all'](cmd, python_shell=False)

    if result['retcode'] not in [0, 1641, 3010]:
        err = 'Running chocolatey failed: {0}'.format(result['stdout'])
        raise CommandExecutionError(err)

    if name == 'chocolatey':
        _clear_context(__context__)

    return result['stdout']