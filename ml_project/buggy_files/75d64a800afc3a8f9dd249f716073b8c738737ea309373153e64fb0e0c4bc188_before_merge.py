def install(pkgs=None,
            requirements=None,
            env=None,
            bin_env=None,
            use_wheel=False,
            log=None,
            proxy=None,
            timeout=None,
            editable=None,
            find_links=None,
            index_url=None,
            extra_index_url=None,
            no_index=False,
            mirrors=None,
            build=None,
            target=None,
            download=None,
            download_cache=None,
            source=None,
            upgrade=False,
            force_reinstall=False,
            ignore_installed=False,
            exists_action=None,
            no_deps=False,
            no_install=False,
            no_download=False,
            global_options=None,
            install_options=None,
            user=None,
            runas=None,
            no_chown=False,
            cwd=None,
            activate=False,
            pre_releases=False,
            __env__='base'):
    '''
    Install packages with pip

    Install packages individually or from a pip requirements file. Install
    packages globally or to a virtualenv.

    pkgs
        comma separated list of packages to install
    requirements
        path to requirements
    bin_env
        path to pip bin or path to virtualenv. If doing a system install,
        and want to use a specific pip bin (pip-2.7, pip-2.6, etc..) just
        specify the pip bin you want.
        If installing into a virtualenv, just use the path to the virtualenv
        (/home/code/path/to/virtualenv/)
    env
        deprecated, use bin_env now
    use_wheel
        Prefer wheel archives (requires pip>=1.4)
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
    editable
        install something editable (i.e.
        git+https://github.com/worldcompany/djangoembed.git#egg=djangoembed)
    find_links
        URL to look for packages at
    index_url
        Base URL of Python Package Index
    extra_index_url
        Extra URLs of package indexes to use in addition to ``index_url``
    no_index
        Ignore package index
    mirrors
        Specific mirror URL(s) to query (automatically adds --use-mirrors)
    build
        Unpack packages into ``build`` dir
    target
        Install packages into ``target`` dir
    download
        Download packages into ``download`` instead of installing them
    download_cache
        Cache downloaded packages in ``download_cache`` dir
    source
        Check out ``editable`` packages into ``source`` dir
    upgrade
        Upgrade all packages to the newest available version
    force_reinstall
        When upgrading, reinstall all packages even if they are already
        up-to-date.
    ignore_installed
        Ignore the installed packages (reinstalling instead)
    exists_action
        Default action when a path already exists: (s)witch, (i)gnore, (w)wipe,
        (b)ackup
    no_deps
        Ignore package dependencies
    no_install
        Download and unpack all packages, but don't actually install them
    no_download
        Don't download any packages, just install the ones
        already downloaded (completes an install run with
        --no-install)
    install_options
        Extra arguments to be supplied to the setup.py install
        command (use like --install-option="--install-
        scripts=/usr/local/bin").  Use multiple --install-
        option options to pass multiple options to setup.py
        install.  If you are using an option with a directory
        path, be sure to use absolute path.
    global_options
        Extra global options to be supplied to the setup.py call before the
        install command.
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
    activate
        Activates the virtual environment, if given via bin_env,
        before running install.
    pre_releases
        Include pre-releases in the available versions


    CLI Example:

    .. code-block:: bash

        salt '*' pip.install <package name>,<package2 name>
        salt '*' pip.install requirements=/path/to/requirements.txt
        salt '*' pip.install <package name> bin_env=/path/to/virtualenv
        salt '*' pip.install <package name> bin_env=/path/to/pip_bin

    Complicated CLI example::

        salt '*' pip.install markdown,django editable=git+https://github.com/worldcompany/djangoembed.git#egg=djangoembed upgrade=True no_deps=True

    '''
    # Switching from using `pip_bin` and `env` to just `bin_env`
    # cause using an env and a pip bin that's not in the env could
    # be problematic.
    # Still using the `env` variable, for backwards compatibility's sake
    # but going fwd you should specify either a pip bin or an env with
    # the `bin_env` argument and we'll take care of the rest.
    if env and not bin_env:
        bin_env = env

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

    cmd = [_get_pip_bin(bin_env), 'install']

    if activate and bin_env:
        if not salt.utils.is_windows():
            cmd = ['.', _get_env_activate(bin_env), '&&'] + cmd

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

    if use_wheel:
        min_version = '1.4'
        cur_version = __salt__['pip.version'](bin_env)
        if not salt.utils.compare_versions(ver1=cur_version, oper='>=',
                                           ver2=min_version):
            log.error(
                ('The --use-wheel option is only supported in pip {0} and '
                 'newer. The version of pip detected is {1}. This option '
                 'will be ignored.'.format(min_version, cur_version))
            )
        else:
            cmd.append('--use-wheel')

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

    if find_links:
        if isinstance(find_links, string_types):
            find_links = [l.strip() for l in find_links.split(',')]

        for link in find_links:
            if not salt.utils.valid_url(link, VALID_PROTOS) or os.path.exists(link):
                raise CommandExecutionError(
                    '{0!r} must be a valid URL or path'.format(link)
                )
            cmd.append('--find-links={0}'.format(link))

    if no_index and (index_url or extra_index_url):
        raise CommandExecutionError(
            '\'no_index\' and (\'index_url\' or \'extra_index_url\') are '
            'mutually exclusive.'
        )

    if index_url:
        if not salt.utils.valid_url(index_url, VALID_PROTOS):
            raise CommandExecutionError(
                '{0!r} must be a valid URL'.format(index_url)
            )
        cmd.append('--index-url={0!r}'.format(index_url))

    if extra_index_url:
        if not salt.utils.valid_url(extra_index_url, VALID_PROTOS):
            raise CommandExecutionError(
                '{0!r} must be a valid URL'.format(extra_index_url)
            )
        cmd.append('--extra-index-url={0!r}'.format(extra_index_url))

    if no_index:
        cmd.append('--no-index')

    if mirrors:
        if isinstance(mirrors, string_types):
            mirrors = [m.strip() for m in mirrors.split(',')]

        cmd.append('--use-mirrors')
        for mirror in mirrors:
            if not mirror.startswith('http://'):
                raise CommandExecutionError(
                    '{0!r} must be a valid URL'.format(mirror)
                )
            cmd.append('--mirrors={0}'.format(mirror))

    if build:
        cmd.append('--build={0}'.format(build))

    if target:
        cmd.append('--target={0}'.format(target))

    if download:
        cmd.append('--download={0}'.format(download))

    if download_cache:
        cmd.append('--download-cache={0}'.format(download_cache))

    if source:
        cmd.append('--source={0}'.format(source))

    if upgrade:
        cmd.append('--upgrade')

    if force_reinstall:
        cmd.append('--force-reinstall')

    if ignore_installed:
        cmd.append('--ignore-installed')

    if exists_action:
        if exists_action.lower() not in ('s', 'i', 'w', 'b'):
            raise CommandExecutionError(
                'The `exists_action`(`--exists-action`) pip option only '
                'allows one of (s, i, w, b) to be passed. The {0!r} value '
                'is not valid.'.format(exists_action)
            )
        cmd.append('--exists-action={0}'.format(exists_action))

    if no_deps:
        cmd.append('--no-deps')

    if no_install:
        cmd.append('--no-install')

    if no_download:
        cmd.append('--no-download')

    if pre_releases:
        # Check the locally installed pip version
        pip_version_cmd = '{0} --version'.format(_get_pip_bin(bin_env))
        output = __salt__['cmd.run_all'](pip_version_cmd).get('stdout', '')
        pip_version = output.split()[1]

        # From pip v1.4 the --pre flag is available
        if salt.utils.compare_versions(ver1=pip_version, oper='>=', ver2='1.4'):
            cmd.append('--pre')

    if global_options:
        if isinstance(global_options, string_types):
            global_options = [go.strip() for go in global_options.split(',')]

        for opt in global_options:
            cmd.append('--global-option={0!r}'.format(opt))

    if install_options:
        if isinstance(install_options, string_types):
            install_options = [io.strip() for io in install_options.split(',')]

        for opt in install_options:
            cmd.append('--install-option={0!r}'.format(opt))

    if pkgs:
        if isinstance(pkgs, string_types):
            pkgs = [p.strip() for p in pkgs.split(',')]

        # It's possible we replaced version-range commas with semicolons so
        # they would survive the previous line (in the pip.installed state).
        # Put the commas back in while making sure the names are contained in
        # quotes, this allows for proper version spec passing salt>=0.17.0
        cmd.extend(
            ['{0!r}'.format(p.replace(';', ',')) for p in pkgs]
        )

    if editable:
        egg_match = re.compile(r'(?:#|#.*?&)egg=([^&]*)')
        if isinstance(editable, string_types):
            editable = [e.strip() for e in editable.split(',')]

        for entry in editable:
            # Is the editable local?
            if not entry.startswith(('file://', '/')):
                match = egg_match.search(entry)

                if not match or not match.group(1):
                    # Missing #egg=theEggName
                    raise CommandExecutionError(
                        'You must specify an egg for this editable'
                    )
            cmd.append('--editable={0}'.format(entry))

    try:
        cmd_kwargs = dict(runas=user, cwd=cwd)
        if bin_env and os.path.isdir(bin_env):
            cmd_kwargs['env'] = {'VIRTUAL_ENV': bin_env}
        return __salt__['cmd.run_all'](' '.join(cmd), **cmd_kwargs)
    finally:
        for requirement in cleanup_requirements:
            try:
                os.remove(requirement)
            except Exception:
                pass