def install(name=None,
            refresh=False,
            sysupgrade=False,
            pkgs=None,
            sources=None,
            **kwargs):
    '''
    .. versionchanged:: 2015.8.12,2016.3.3,2016.11.0
        On minions running systemd>=205, `systemd-run(1)`_ is now used to
        isolate commands which modify installed packages from the
        ``salt-minion`` daemon's control group. This is done to keep systemd
        from killing any pacman commands spawned by Salt when the
        ``salt-minion`` service is restarted. (see ``KillMode`` in the
        `systemd.kill(5)`_ manpage for more information). If desired, usage of
        `systemd-run(1)`_ can be suppressed by setting a :mod:`config option
        <salt.modules.config.get>` called ``systemd.scope``, with a value of
        ``False`` (no quotes).

    .. _`systemd-run(1)`: https://www.freedesktop.org/software/systemd/man/systemd-run.html
    .. _`systemd.kill(5)`: https://www.freedesktop.org/software/systemd/man/systemd.kill.html

    Install (``pacman -S``) the specified packag(s). Add ``refresh=True`` to
    install with ``-y``, add ``sysupgrade=True`` to install with ``-u``.

    name
        The name of the package to be installed. Note that this parameter is
        ignored if either ``pkgs`` or ``sources`` is passed. Additionally,
        please note that this option can only be used to install packages from
        a software repository. To install a package file manually, use the
        ``sources`` option.

        CLI Example:

        .. code-block:: bash

            salt '*' pkg.install <package name>

    refresh
        Whether or not to refresh the package database before installing.

    sysupgrade
        Whether or not to upgrade the system packages before installing.


    Multiple Package Installation Options:

    pkgs
        A list of packages to install from a software repository. Must be
        passed as a python list. A specific version number can be specified
        by using a single-element dict representing the package and its
        version. As with the ``version`` parameter above, comparison operators
        can be used to target a specific version of a package.

        CLI Examples:

        .. code-block:: bash

            salt '*' pkg.install pkgs='["foo", "bar"]'
            salt '*' pkg.install pkgs='["foo", {"bar": "1.2.3-4"}]'
            salt '*' pkg.install pkgs='["foo", {"bar": "<1.2.3-4"}]'

    sources
        A list of packages to install. Must be passed as a list of dicts,
        with the keys being package names, and the values being the source URI
        or local path to the package.

        CLI Example:

        .. code-block:: bash

            salt '*' pkg.install \
                sources='[{"foo": "salt://foo.pkg.tar.xz"}, \
                {"bar": "salt://bar.pkg.tar.xz"}]'


    Returns a dict containing the new package names and versions::

        {'<package>': {'old': '<old-version>',
                       'new': '<new-version>'}}
    '''
    refresh = salt.utils.is_true(refresh)
    sysupgrade = salt.utils.is_true(sysupgrade)

    try:
        pkg_params, pkg_type = __salt__['pkg_resource.parse_targets'](
            name, pkgs, sources, **kwargs
        )
    except MinionError as exc:
        raise CommandExecutionError(exc)

    if pkg_params is None or len(pkg_params) == 0:
        return {}

    if 'root' in kwargs:
        pkg_params['-r'] = kwargs['root']

    cmd = []
    if salt.utils.systemd.has_scope(__context__) \
            and __salt__['config.get']('systemd.scope', True):
        cmd.extend(['systemd-run', '--scope'])
    cmd.append('pacman')

    errors = []
    if pkg_type == 'file':
        cmd.extend(['-U', '--noprogressbar', '--noconfirm'])
        cmd.extend(pkg_params)
    elif pkg_type == 'repository':
        cmd.append('-S')
        if refresh:
            cmd.append('-y')
        if sysupgrade:
            cmd.append('-u')
        cmd.extend(['--noprogressbar', '--noconfirm', '--needed'])
        targets = []
        wildcards = []
        for param, version_num in six.iteritems(pkg_params):
            if version_num is None:
                targets.append(param)
            else:
                match = re.match('^([<>])?(=)?([^<>=]+)$', version_num)
                if match:
                    gt_lt, eq, verstr = match.groups()
                    prefix = gt_lt or ''
                    prefix += eq or ''
                    # If no prefix characters were supplied, use '='
                    prefix = prefix or '='
                    if '*' in verstr:
                        if prefix == '=':
                            wildcards.append((param, verstr))
                        else:
                            errors.append(
                                'Invalid wildcard for {0}{1}{2}'.format(
                                    param, prefix, verstr
                                )
                            )
                        continue
                    targets.append('{0}{1}{2}'.format(param, prefix, verstr))
                else:
                    errors.append(
                        'Invalid version string \'{0}\' for package '
                        '\'{1}\''.format(version_num, name)
                    )

        if wildcards:
            # Resolve wildcard matches
            _available = list_repo_pkgs(*[x[0] for x in wildcards], refresh=refresh)
            for pkgname, verstr in wildcards:
                candidates = _available.get(pkgname, [])
                match = salt.utils.fnmatch_multiple(candidates, verstr)
                if match is not None:
                    targets.append('='.join((pkgname, match)))
                else:
                    errors.append(
                        'No version matching \'{0}\' found for package \'{1}\' '
                        '(available: {2})'.format(
                            verstr,
                            pkgname,
                            ', '.join(candidates) if candidates else 'none'
                        )
                    )

            if refresh:
                try:
                    # Prevent a second refresh when we run the install command
                    cmd.remove('-y')
                except ValueError:
                    # Shouldn't happen since we only add -y when refresh is True,
                    # but just in case that code above is inadvertently changed,
                    # don't let this result in a traceback.
                    pass

    if not errors:
        cmd.extend(targets)
        old = list_pkgs()
        out = __salt__['cmd.run_all'](
            cmd,
            output_loglevel='trace',
            python_shell=False
        )

        if out['retcode'] != 0 and out['stderr']:
            errors = [out['stderr']]
        else:
            errors = []

        __context__.pop('pkg.list_pkgs', None)
        new = list_pkgs()
        ret = salt.utils.compare_dicts(old, new)

    if errors:
        try:
            changes = ret
        except UnboundLocalError:
            # We ran into errors before we attempted to install anything, so
            # there are no changes.
            changes = {}
        raise CommandExecutionError(
            'Problem encountered installing package(s)',
            info={'errors': errors, 'changes': changes}
        )

    return ret