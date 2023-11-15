def uninstall(pkgs=None,
              requirements=None,
              bin_env=None,
              log=None,
              proxy=None,
              timeout=None,
              user=None,
              runas=None,
              no_chown=False,
              cwd=None,
              __env__='base'):
    '''
    Uninstall packages with pip

    Uninstall packages individually or from a pip requirements file. Uninstall
    packages globally or from a virtualenv.

    pkgs
        comma separated list of packages to install
    requirements
        path to requirements
    bin_env
        path to pip bin or path to virtualenv. If doing an uninstall from
        the system python and want to use a specific pip bin (pip-2.7,
        pip-2.6, etc..) just specify the pip bin you want.
        If uninstalling from a virtualenv, just use the path to the virtualenv
        (/home/code/path/to/virtualenv/)
    log
        Log file where a complete (maximum verbosity) record will be kept
    proxy
        Specify a proxy in the form
        user:passwd@proxy.server:port. Note that the
        user:password@ is optional and required only if you
        are behind an authenticated proxy.  If you provide
        user@proxy.server:port then you will be prompted for a
        password.
    timeout
        Set the socket timeout (default 15 seconds)
    user
        The user under which to run pip

    .. note::
        The ``runas`` argument is deprecated as of 0.16.2. ``user`` should be
        used instead.

    no_chown
        When user is given, do not attempt to copy and chown
        a requirements file
    cwd
        Current working directory to run pip from

    CLI Example:

    .. code-block:: bash

        salt '*' pip.uninstall <package name>,<package2 name>
        salt '*' pip.uninstall requirements=/path/to/requirements.txt
        salt '*' pip.uninstall <package name> bin_env=/path/to/virtualenv
        salt '*' pip.uninstall <package name> bin_env=/path/to/pip_bin

    '''
    cmd = [_get_pip_bin(bin_env), 'uninstall', '-y']

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

    cleanup_requirements = []
    if requirements is not None:
        if isinstance(requirements, string_types):
            requirements = [r.strip() for r in requirements.split(',')]

        for requirement in requirements:
            treq = None
            if requirement.startswith('salt://'):
                cached_requirements = _get_cached_requirements(
                    requirement, __env__
                )
                if not cached_requirements:
                    return {
                        'result': False,
                        'comment': (
                            'pip requirements file {0!r} not found'.format(
                                requirement
                            )
                        )
                    }
                requirement = cached_requirements

            if user and not no_chown:
                # Need to make a temporary copy since the user will, most
                # likely, not have the right permissions to read the file
                treq = salt.utils.mkstemp()
                shutil.copyfile(requirement, treq)
                logger.debug(
                    'Changing ownership of requirements file {0!r} to '
                    'user {1!r}'.format(treq, user)
                )
                __salt__['file.chown'](treq, user, None)
                cleanup_requirements.append(treq)
            cmd.append('--requirement={0!r}'.format(treq or requirement))

    if log:
        try:
            # TODO make this check if writeable
            os.path.exists(log)
        except IOError:
            raise IOError('{0!r} is not writeable'.format(log))

        cmd.append('--log={0}'.format(log))

    if proxy:
        cmd.append('--proxy={0!r}'.format(proxy))

    if timeout:
        try:
            int(timeout)
        except ValueError:
            raise ValueError(
                '{0!r} is not a valid integer base 10.'.format(timeout)
            )
        cmd.append('--timeout={0}'.format(timeout))

    if pkgs:
        if isinstance(pkgs, string_types):
            pkgs = [p.strip() for p in pkgs.split(',')]
        cmd.extend(pkgs)

    cmd_kwargs = dict(runas=user, cwd=cwd)
    if bin_env and os.path.isdir(bin_env):
        cmd_kwargs['env'] = {'VIRTUAL_ENV': bin_env}

    try:
        return __salt__['cmd.run_all'](' '.join(cmd), **cmd_kwargs)
    finally:
        for requirement in cleanup_requirements:
            try:
                os.remove(requirement)
            except Exception:
                pass