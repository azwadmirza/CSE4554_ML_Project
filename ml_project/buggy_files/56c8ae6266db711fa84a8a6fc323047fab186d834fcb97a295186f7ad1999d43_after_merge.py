def install_missing(name, version=None, source=None):
    '''
    Instructs Chocolatey to install a package if it doesn't already exist.

    .. versionchanged:: 2014.7.0
        If the minion has Chocolatey >= 0.9.8.24 installed, this function calls
        :mod:`chocolatey.install <salt.modules.chocolatey.install>` instead, as
        ``installmissing`` is deprecated as of that version and will be removed
        in Chocolatey 1.0.

    name
        The name of the package to be installed. Only accepts a single argument.

    version
        Install a specific version of the package. Defaults to latest version
        available.

    source
        Chocolatey repository (directory, share or remote URL feed) the package
        comes from. Defaults to the official Chocolatey feed.

    CLI Example:

    .. code-block:: bash

        salt '*' chocolatey.install_missing <package name>
        salt '*' chocolatey.install_missing <package name> version=<package version>
    '''
    if _LooseVersion(chocolatey_version()) >= _LooseVersion('0.9.8.24'):
        log.warning('installmissing is deprecated, using install')
        return install(name, version=version)

    # chocolatey helpfully only supports a single package argument
    cmd = [_find_chocolatey(), 'installmissing', name]
    if version:
        cmd.extend(['--version', version])
    if source:
        cmd.extend(['--source', source])
    # Shouldn't need this as this code should never run on v0.9.9 and newer
    cmd.extend(_yes())
    result = __salt__['cmd.run_all'](cmd, python_shell=False)

    if result['retcode'] != 0:
        err = 'Running chocolatey failed: {0}'.format(result['stdout'])
        raise CommandExecutionError(err)

    return result['stdout']