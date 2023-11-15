def freeze(bin_env=None,
           user=None,
           runas=None,
           cwd=None):
    '''
    Return a list of installed packages either globally or in the specified
    virtualenv

    bin_env
        path to pip bin or path to virtualenv. If doing an uninstall from
        the system python and want to use a specific pip bin (pip-2.7,
        pip-2.6, etc..) just specify the pip bin you want.
        If uninstalling from a virtualenv, just use the path to the virtualenv
        (/home/code/path/to/virtualenv/)
    user
        The user under which to run pip

    .. note::
        The ``runas`` argument is deprecated as of 0.16.2. ``user`` should be
        used instead.

    cwd
        Current working directory to run pip from

    CLI Example:

    .. code-block:: bash

        salt '*' pip.freeze /home/code/path/to/virtualenv/
    '''
    if runas is not None:
        # The user is using a deprecated argument, warn!
        salt.utils.warn_until(
            (0, 18),
            'The \'runas\' argument to pip.install is deprecated, and will be '
            'removed in 0.18.0. Please use \'user\' instead.'
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

    cmd = [_get_pip_bin(bin_env), 'freeze']
    cmd_kwargs = dict(runas=user, cwd=cwd)
    if bin_env and os.path.isdir(bin_env):
        cmd_kwargs['env'] = {'VIRTUAL_ENV': bin_env}
    result = __salt__['cmd.run_all'](' '.join(cmd), **cmd_kwargs)

    if result['retcode'] > 0:
        raise CommandExecutionError(result['stderr'])

    return result['stdout'].splitlines()