def install(pkgs=None,  # pylint: disable=R0912,R0913,R0914
            requirements=None,
            env=None,
            bin_env=None,
            use_wheel=False,
            no_use_wheel=False,
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
            no_chown=False,
            cwd=None,
            activate=False,
            pre_releases=False,
            cert=None,
            allow_all_external=False,
            allow_external=None,
            allow_unverified=None,
            process_dependency_links=False,
            __env__=None,
            saltenv='base',
            env_vars=None,
            use_vt=False,
            trusted_host=None):
    '''
    Install packages with pip

    Install packages individually or from a pip requirements file. Install
    packages globally or to a virtualenv.

    pkgs
        Comma separated list of packages to install

    requirements
        Path to requirements

    bin_env
        Path to pip bin or path to virtualenv. If doing a system install,
        and want to use a specific pip bin (pip-2.7, pip-2.6, etc..) just
        specify the pip bin you want.

        .. note::
            If installing into a virtualenv, just use the path to the
            virtualenv (e.g. ``/home/code/path/to/virtualenv/``)

    env
        Deprecated, use bin_env now

    use_wheel
        Prefer wheel archives (requires pip>=1.4)

    no_use_wheel
        Force to not use wheel archives (requires pip>=1.4)

    log
        Log file where a complete (maximum verbosity) record will be kept

    proxy
        Specify a proxy in the form ``user:passwd@proxy.server:port``. Note
        that the ``user:password@`` is optional and required only if you are
        behind an authenticated proxy. If you provide
        ``user@proxy.server:port`` then you will be prompted for a password.

    timeout
        Set the socket timeout (default 15 seconds)

    editable
        install something editable (e.g.
        ``git+https://github.com/worldcompany/djangoembed.git#egg=djangoembed``)

    find_links
        URL to search for packages

    index_url
        Base URL of Python Package Index

    extra_index_url
        Extra URLs of package indexes to use in addition to ``index_url``

    no_index
        Ignore package index

    mirrors
        Specific mirror URL(s) to query (automatically adds --use-mirrors)

        .. warning::

            This option has been deprecated and removed in pip version 7.0.0.
            Please use ``index_url`` and/or ``extra_index_url`` instead.

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
        Default action when a path already exists: (s)witch, (i)gnore, (w)ipe,
        (b)ackup

    no_deps
        Ignore package dependencies

    no_install
        Download and unpack all packages, but don't actually install them

    no_download
        Don't download any packages, just install the ones already downloaded
        (completes an install run with ``--no-install``)

    install_options
        Extra arguments to be supplied to the setup.py install command (e.g.
        like ``--install-option='--install-scripts=/usr/local/bin'``).  Use
        multiple --install-option options to pass multiple options to setup.py
        install. If you are using an option with a directory path, be sure to
        use absolute path.

    global_options
        Extra global options to be supplied to the setup.py call before the
        install command.

    user
        The user under which to run pip

    no_chown
        When user is given, do not attempt to copy and chown a requirements
        file

    cwd
        Current working directory to run pip from

    activate
        Activates the virtual environment, if given via bin_env, before running
        install.

        .. deprecated:: 2014.7.2
            If `bin_env` is given, pip will already be sourced from that
            virtualenv, making `activate` effectively a noop.

    pre_releases
        Include pre-releases in the available versions

    cert
        Provide a path to an alternate CA bundle

    allow_all_external
        Allow the installation of all externally hosted files

    allow_external
        Allow the installation of externally hosted files (comma separated
        list)

    allow_unverified
        Allow the installation of insecure and unverifiable files (comma
        separated list)

    process_dependency_links
        Enable the processing of dependency links

    env_vars
        Set environment variables that some builds will depend on. For example,
        a Python C-module may have a Makefile that needs INCLUDE_PATH set to
        pick up a header file while compiling.  This must be in the form of a
        dictionary or a mapping.

        Example:

        .. code-block:: bash

            salt '*' pip.install django_app env_vars="{'CUSTOM_PATH': '/opt/django_app'}"

    trusted_host
        Mark this host as trusted, even though it does not have valid or any
        HTTPS.

    use_vt
        Use VT terminal emulation (see output while installing)

    CLI Example:

    .. code-block:: bash

        salt '*' pip.install <package name>,<package2 name>
        salt '*' pip.install requirements=/path/to/requirements.txt
        salt '*' pip.install <package name> bin_env=/path/to/virtualenv
        salt '*' pip.install <package name> bin_env=/path/to/pip_bin

    Complicated CLI example::

        salt '*' pip.install markdown,django \
                editable=git+https://github.com/worldcompany/djangoembed.git#egg=djangoembed upgrade=True no_deps=True

    '''
    # Switching from using `pip_bin` and `env` to just `bin_env`
    # cause using an env and a pip bin that's not in the env could
    # be problematic.
    # Still using the `env` variable, for backwards compatibility's sake
    # but going fwd you should specify either a pip bin or an env with
    # the `bin_env` argument and we'll take care of the rest.
    if env and not bin_env:
        salt.utils.warn_until(
            'Carbon',
            'Passing \'env\' to the pip module is deprecated. Use bin_env instead. '
            'This functionality will be removed in Salt Carbon.'
        )
        bin_env = env

    if activate:
        salt.utils.warn_until(
            'Carbon',
            'Passing \'activate\' to the pip module is deprecated. If '
            'bin_env refers to a virtualenv, there is no need to activate '
            'that virtualenv before using pip to install packages in it.'
        )

    if isinstance(__env__, string_types):
        salt.utils.warn_until(
            'Carbon',
            'Passing a salt environment should be done using \'saltenv\' '
            'not \'__env__\'. This functionality will be removed in Salt '
            'Carbon.'
        )
        # Backwards compatibility
        saltenv = __env__

    pip_bin = _get_pip_bin(bin_env)

    cmd = [pip_bin, 'install']

    cleanup_requirements, error = _process_requirements(
        requirements=requirements,
        cmd=cmd,
        cwd=cwd,
        saltenv=saltenv,
        user=user
    )

    if error:
        return error

    if use_wheel:
        min_version = '1.4'
        cur_version = __salt__['pip.version'](bin_env)
        if not salt.utils.compare_versions(ver1=cur_version, oper='>=',
                                           ver2=min_version):
            logger.error(
                ('The --use-wheel option is only supported in pip {0} and '
                 'newer. The version of pip detected is {1}. This option '
                 'will be ignored.'.format(min_version, cur_version))
            )
        else:
            cmd.append('--use-wheel')

    if no_use_wheel:
        min_version = '1.4'
        cur_version = __salt__['pip.version'](bin_env)
        if not salt.utils.compare_versions(ver1=cur_version, oper='>=',
                                           ver2=min_version):
            logger.error(
                ('The --no-use-wheel option is only supported in pip {0} and '
                 'newer. The version of pip detected is {1}. This option '
                 'will be ignored.'.format(min_version, cur_version))
            )
        else:
            cmd.append('--no-use-wheel')

    if log:
        if os.path.isdir(log):
            raise IOError(
                '\'{0}\' is a directory. Use --log path_to_file'.format(log))
        elif not os.access(log, os.W_OK):
            raise IOError('\'{0}\' is not writeable'.format(log))

        cmd.extend(['--log', log])

    if proxy:
        cmd.extend(['--proxy', proxy])

    if timeout:
        try:
            if isinstance(timeout, float):
                # Catch floating point input, exception will be caught in
                # exception class below.
                raise ValueError('Timeout cannot be a float')
            int(timeout)
        except ValueError:
            raise ValueError(
                '\'{0}\' is not a valid timeout, must be an integer'
                .format(timeout)
            )
        cmd.extend(['--timeout', timeout])

    if find_links:
        if isinstance(find_links, string_types):
            find_links = [l.strip() for l in find_links.split(',')]

        for link in find_links:
            if not (salt.utils.url.validate(link, VALID_PROTOS) or os.path.exists(link)):
                raise CommandExecutionError(
                    '\'{0}\' is not a valid URL or path'.format(link)
                )
            cmd.extend(['--find-links', link])

    if no_index and (index_url or extra_index_url):
        raise CommandExecutionError(
            '\'no_index\' and (\'index_url\' or \'extra_index_url\') are '
            'mutually exclusive.'
        )

    if index_url:
        if not salt.utils.url.validate(index_url, VALID_PROTOS):
            raise CommandExecutionError(
                '\'{0}\' is not a valid URL'.format(index_url)
            )
        cmd.extend(['--index-url', index_url])

    if extra_index_url:
        if not salt.utils.url.validate(extra_index_url, VALID_PROTOS):
            raise CommandExecutionError(
                '\'{0}\' is not a valid URL'.format(extra_index_url)
            )
        cmd.extend(['--extra-index-url', extra_index_url])

    if no_index:
        cmd.append('--no-index')

    if mirrors:
        # https://github.com/pypa/pip/pull/2641/files#diff-3ef137fb9ffdd400f117a565cd94c188L216
        pip_version = version(pip_bin)
        if salt.utils.compare_versions(ver1=pip_version, oper='>=', ver2='7.0.0'):
            raise CommandExecutionError(
                    'pip >= 7.0.0 does not support mirror argument:'
                    ' use index_url and/or extra_index_url instead'
            )

        if isinstance(mirrors, string_types):
            mirrors = [m.strip() for m in mirrors.split(',')]

        cmd.append('--use-mirrors')
        for mirror in mirrors:
            if not mirror.startswith('http://'):
                raise CommandExecutionError(
                    '\'{0}\' is not a valid URL'.format(mirror)
                )
            cmd.extend(['--mirrors', mirror])

    if build:
        cmd.extend(['--build', build])

    if target:
        cmd.extend(['--target', target])

    if download:
        cmd.extend(['--download', download])

    if download_cache:
        cmd.extend(['--download-cache', download_cache])

    if source:
        cmd.extend(['--source', source])

    if upgrade:
        cmd.append('--upgrade')

    if force_reinstall:
        cmd.append('--force-reinstall')

    if ignore_installed:
        cmd.append('--ignore-installed')

    if exists_action:
        if exists_action.lower() not in ('s', 'i', 'w', 'b'):
            raise CommandExecutionError(
                'The exists_action pip option only supports the values '
                's, i, w, and b. \'{0}\' is not valid.'.format(exists_action)
            )
        cmd.extend(['--exists-action', exists_action])

    if no_deps:
        cmd.append('--no-deps')

    if no_install:
        cmd.append('--no-install')

    if no_download:
        cmd.append('--no-download')

    if pre_releases:
        # Check the locally installed pip version
        pip_version = version(pip_bin)

        # From pip v1.4 the --pre flag is available
        if salt.utils.compare_versions(ver1=pip_version, oper='>=', ver2='1.4'):
            cmd.append('--pre')

    if cert:
        cmd.extend(['--cert', cert])

    if global_options:
        if isinstance(global_options, string_types):
            global_options = [go.strip() for go in global_options.split(',')]

        for opt in global_options:
            cmd.extend(['--global-option', opt])

    if install_options:
        if isinstance(install_options, string_types):
            install_options = [io.strip() for io in install_options.split(',')]

        for opt in install_options:
            cmd.extend(['--install-option', opt])

    if pkgs:
        if isinstance(pkgs, string_types):
            pkgs = [p.strip() for p in pkgs.split(',')]

        # It's possible we replaced version-range commas with semicolons so
        # they would survive the previous line (in the pip.installed state).
        # Put the commas back in while making sure the names are contained in
        # quotes, this allows for proper version spec passing salt>=0.17.0
        cmd.extend(['{0}'.format(p.replace(';', ',')) for p in pkgs])

    if editable:
        egg_match = re.compile(r'(?:#|#.*?&)egg=([^&]*)')
        if isinstance(editable, string_types):
            editable = [e.strip() for e in editable.split(',')]

        for entry in editable:
            # Is the editable local?
            if not (entry == '.' or entry.startswith(('file://', '/'))):
                match = egg_match.search(entry)

                if not match or not match.group(1):
                    # Missing #egg=theEggName
                    raise CommandExecutionError(
                        'You must specify an egg for this editable'
                    )
            cmd.extend(['--editable', entry])

    if allow_all_external:
        cmd.append('--allow-all-external')

    if allow_external:
        if isinstance(allow_external, string_types):
            allow_external = [p.strip() for p in allow_external.split(',')]

        for pkg in allow_external:
            cmd.extend(['--allow-external', pkg])

    if allow_unverified:
        if isinstance(allow_unverified, string_types):
            allow_unverified = \
                [p.strip() for p in allow_unverified.split(',')]

        for pkg in allow_unverified:
            cmd.extend(['--allow-unverified', pkg])

    if process_dependency_links:
        cmd.append('--process-dependency-links')

    if env_vars:
        if isinstance(env_vars, dict):
            for k, v in iteritems(env_vars):
                if not isinstance(v, string_types):
                    env_vars[k] = str(v)
            os.environ.update(env_vars)
        else:
            raise CommandExecutionError(
                'env_vars {0} is not a dictionary'.format(env_vars))

    if trusted_host:
        cmd.extend(['--trusted-host', trusted_host])

    try:
        cmd_kwargs = dict(saltenv=saltenv, use_vt=use_vt, runas=user)

        if cwd:
            cmd_kwargs['cwd'] = cwd

        if bin_env and os.path.isdir(bin_env):
            cmd_kwargs['env'] = {'VIRTUAL_ENV': bin_env}

        logger.debug(
            'TRY BLOCK: end of pip.install -- cmd: %s, cmd_kwargs: %s',
            str(cmd), str(cmd_kwargs)
        )

        return __salt__['cmd.run_all'](cmd,
                                       python_shell=False,
                                       **cmd_kwargs)
    finally:
        for tempdir in [cr for cr in cleanup_requirements if cr is not None]:
            if os.path.isdir(tempdir):
                shutil.rmtree(tempdir)