def list_(prefix=None,
          bin_env=None,
          user=None,
          runas=None,
          cwd=None):
    '''
    Filter list of installed apps from ``freeze`` and check to see if
    ``prefix`` exists in the list of packages installed.

    CLI Example:

    .. code-block:: bash

        salt '*' pip.list salt
    '''
    packages = {}

    pip_bin = _get_pip_bin(bin_env)
    pip_version_cmd = [pip_bin, '--version']
    cmd = [pip_bin, 'freeze']

    if runas is not None:
        # The user is using a deprecated argument, warn!
        salt.utils.warn_until(
            'Hydrogen',
            'The \'runas\' argument to pip.install is deprecated, and will be '
            'removed in Salt {version}. Please use \'user\' instead.'
        )

    # "There can only be one"
    if runas is not None and user:
        raise CommandExecutionError(
            'The \'runas\' and \'user\' arguments are mutually exclusive. '
            'Please use \'user\' as \'runas\' is being deprecated.'
        )

    # Support deprecated 'runas' arg
    elif runas is not None and not user:
        user = str(runas)

    cmd_kwargs = dict(runas=user, cwd=cwd)
    if bin_env and os.path.isdir(bin_env):
        cmd_kwargs['env'] = {'VIRTUAL_ENV': bin_env}

    if not prefix or prefix in ('p', 'pi', 'pip'):
        pip_version_result = __salt__['cmd.run_all'](' '.join(pip_version_cmd),
                                                     **cmd_kwargs)
        if pip_version_result['retcode'] > 0:
            raise CommandExecutionError(pip_version_result['stderr'])
        packages['pip'] = pip_version_result['stdout'].split()[1]

    result = __salt__['cmd.run_all'](' '.join(cmd), **cmd_kwargs)
    if result['retcode'] > 0:
        raise CommandExecutionError(result['stderr'])

    for line in result['stdout'].splitlines():
        if line.startswith('-f'):
            # ignore -f line as it contains --find-links directory
            continue
        elif line.startswith('-e'):
            line = line.split('-e ')[1]
            version_, name = line.split('#egg=')
        elif len(line.split('==')) >= 2:
            name = line.split('==')[0]
            version_ = line.split('==')[1]
        else:
            logger.error("Can't parse line '%s'", line)
            continue

        if prefix:
            if name.lower().startswith(prefix.lower()):
                packages[name] = version_
        else:
            packages[name] = version_
    return packages