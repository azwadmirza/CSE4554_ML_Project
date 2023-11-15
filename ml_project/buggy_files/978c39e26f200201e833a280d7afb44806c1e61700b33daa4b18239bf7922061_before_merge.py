def update(name, source=None, pre_versions=False):
    '''
    Instructs Chocolatey to update packages on the system.

    name
        The name of the package to update, or "all" to update everything
        installed on the system.

    source
        Chocolatey repository (directory, share or remote URL feed) the package
        comes from. Defaults to the official Chocolatey feed.

    pre_versions
        Include pre-release packages in comparison. Defaults to False.

    CLI Example:

    .. code-block:: bash

        salt "*" chocolatey.update all
        salt "*" chocolatey.update <package name> pre_versions=True
    '''
    # chocolatey helpfully only supports a single package argument
    choc_path = _find_chocolatey(__context__, __salt__)
    if _LooseVersion(chocolatey_version()) >= _LooseVersion('0.9.8.24'):
        log.warning('update is deprecated, using upgrade')
        return upgrade(name, source=source, pre_versions=pre_versions)

    cmd = [choc_path, 'update', name]
    if source:
        cmd.extend(['--source', source])
    if salt.utils.is_true(pre_versions):
        cmd.append('--prerelease')
    cmd.extend(_yes(__context__))
    result = __salt__['cmd.run_all'](cmd, python_shell=False)

    if result['retcode'] not in [0, 1641, 3010]:
        err = 'Running chocolatey failed: {0}'.format(result['stdout'])
        raise CommandExecutionError(err)

    return result['stdout']