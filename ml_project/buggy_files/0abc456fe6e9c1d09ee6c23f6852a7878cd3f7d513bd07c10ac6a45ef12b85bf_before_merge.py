def list_(narrow=None,
          all_versions=False,
          pre_versions=False,
          source=None,
          local_only=False,
          exact=False):
    '''
    Instructs Chocolatey to pull a vague package list from the repository.

    Args:

        narrow (str):
            Term used to narrow down results. Searches against
            name/description/tag. Default is None.

        all_versions (bool):
            Display all available package versions in results. Default is False.

        pre_versions (bool):
            Display pre-release packages in results. Default is False.

        source (str):
            Chocolatey repository (directory, share or remote URL feed) the
            package comes from. Defaults to the official Chocolatey feed if
            None is passed. Default is None.

        local_only (bool):
            Display packages only installed locally. Default is False.

        exact (bool):
            Display only packages that match ``narrow`` exactly. Default is
            False.

            .. versionadded:: 2017.7.0

    Returns:
        dict: A dictionary of results.

    CLI Example:

    .. code-block:: bash

        salt '*' chocolatey.list <narrow>
        salt '*' chocolatey.list <narrow> all_versions=True
    '''
    choc_path = _find_chocolatey(__context__, __salt__)
    cmd = [choc_path, 'list']
    if narrow:
        cmd.append(narrow)
    if salt.utils.is_true(all_versions):
        cmd.append('--allversions')
    if salt.utils.is_true(pre_versions):
        cmd.append('--prerelease')
    if source:
        cmd.extend(['--source', source])
    if local_only:
        cmd.append('--local-only')
    if exact:
        cmd.append('--exact')

    # This is needed to parse the output correctly
    cmd.append('--limit-output')

    result = __salt__['cmd.run_all'](cmd, python_shell=False)

    if result['retcode'] != 0:
        err = 'Running chocolatey failed: {0}'.format(result['stdout'])
        raise CommandExecutionError(err)

    ret = {}
    pkg_re = re.compile(r'(\S+)\|(\S+)')
    for line in result['stdout'].split('\n'):
        if line.startswith("No packages"):
            return ret
        for name, ver in pkg_re.findall(line):
            if 'chocolatey' in name:
                continue
            if name not in ret:
                ret[name] = []
            ret[name].append(ver)

    return ret