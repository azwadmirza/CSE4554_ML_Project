def installed(
        name,
        version=None,
        refresh=None,
        fromrepo=None,
        skip_verify=False,
        skip_suggestions=False,
        pkgs=None,
        sources=None,
        allow_updates=False,
        pkg_verify=False,
        normalize=True,
        ignore_epoch=False,
        reinstall=False,
        update_holds=False,
        **kwargs):
    '''
    Ensure that the package is installed, and that it is the correct version
    (if specified).

    :param str name:
        The name of the package to be installed. This parameter is ignored if
        either "pkgs" or "sources" is used. Additionally, please note that this
        option can only be used to install packages from a software repository.
        To install a package file manually, use the "sources" option detailed
        below.

    :param str version:
        Install a specific version of a package. This option is ignored if
        "sources" is used. Currently, this option is supported
        for the following pkg providers: :mod:`apt <salt.modules.aptpkg>`,
        :mod:`ebuild <salt.modules.ebuild>`,
        :mod:`pacman <salt.modules.pacman>`,
        :mod:`win_pkg <salt.modules.win_pkg>`,
        :mod:`yumpkg <salt.modules.yumpkg>`, and
        :mod:`zypper <salt.modules.zypper>`. The version number includes the
        release designation where applicable, to allow Salt to target a
        specific release of a given version. When in doubt, using the
        ``pkg.latest_version`` function for an uninstalled package will tell
        you the version available.

        .. code-block:: bash

            # salt myminion pkg.latest_version vim-enhanced
            myminion:
                2:7.4.160-1.el7

        .. important::
            As of version 2015.8.7, for distros which use yum/dnf, packages
            which have a version with a nonzero epoch (that is, versions which
            start with a number followed by a colon like in the
            ``pkg.latest_version`` output above) must have the epoch included
            when specifying the version number. For example:

            .. code-block:: yaml

                vim-enhanced:
                  pkg.installed:
                    - version: 2:7.4.160-1.el7

            In version 2015.8.9, an **ignore_epoch** argument has been added to
            :py:mod:`pkg.installed <salt.states.pkg.installed>`,
            :py:mod:`pkg.removed <salt.states.pkg.installed>`, and
            :py:mod:`pkg.purged <salt.states.pkg.installed>` states, which
            causes the epoch to be disregarded when the state checks to see if
            the desired version was installed.

        Also, while this function is not yet implemented for all pkg frontends,
        :mod:`pkg.list_repo_pkgs <salt.modules.yumpkg.list_repo_pkgs>` will
        show all versions available in the various repositories for a given
        package, irrespective of whether or not it is installed.

        .. code-block:: bash

            # salt myminion pkg.list_repo_pkgs bash
            myminion:
            ----------
                bash:
                    - 4.2.46-21.el7_3
                    - 4.2.46-20.el7_2

        This function was first added for :mod:`pkg.list_repo_pkgs
        <salt.modules.yumpkg.list_repo_pkgs>` in 2014.1.0, and was expanded to
        :py:func:`Debian/Ubuntu <salt.modules.aptpkg.list_repo_pkgs>` and
        :py:func:`Arch Linux <salt.modules.pacman.list_repo_pkgs>`-based
        distros in the Nitrogen release.

        The version strings returned by either of these functions can be used
        as version specifiers in pkg states.

        You can install a specific version when using the ``pkgs`` argument by
        including the version after the package:

        .. code-block:: yaml

            common_packages:
              pkg.installed:
                - pkgs:
                  - unzip
                  - dos2unix
                  - salt-minion: 2015.8.5-1.el6

        If the version given is the string ``latest``, the latest available
        package version will be installed à la ``pkg.latest``.

        **WILDCARD VERSIONS**

        As of the Nitrogen release, this state now supports wildcards in
        package versions for SUSE SLES/Leap/Tumbleweed, Debian/Ubuntu, RHEL/CentOS,
        Arch Linux, and their derivatives. Using wildcards can be useful for
        packages where the release name is built into the version in some way,
        such as for RHEL/CentOS which typically has version numbers like
        ``1.2.34-5.el7``. An example of the usage for this would be:

        .. code-block:: yaml

            mypkg:
              pkg.installed:
                - version: '1.2.34*'

    :param bool refresh:
        This parameter controls whether or not the package repo database is
        updated prior to installing the requested package(s).

        If ``True``, the package database will be refreshed (``apt-get
        update`` or equivalent, depending on platform) before installing.

        If ``False``, the package database will *not* be refreshed before
        installing.

        If unset, then Salt treats package database refreshes differently
        depending on whether or not a ``pkg`` state has been executed already
        during the current Salt run. Once a refresh has been performed in a
        ``pkg`` state, for the remainder of that Salt run no other refreshes
        will be performed for ``pkg`` states which do not explicitly set
        ``refresh`` to ``True``. This prevents needless additional refreshes
        from slowing down the Salt run.

    :param str cache_valid_time:

        .. versionadded:: 2016.11.0

        This parameter sets the value in seconds after which the cache is
        marked as invalid, and a cache update is necessary. This overwrites
        the ``refresh`` parameter's default behavior.

        Example:

        .. code-block:: yaml

            httpd:
              pkg.installed:
                - fromrepo: mycustomrepo
                - skip_verify: True
                - skip_suggestions: True
                - version: 2.0.6~ubuntu3
                - refresh: True
                - cache_valid_time: 300
                - allow_updates: True
                - hold: False

        In this case, a refresh will not take place for 5 minutes since the last
        ``apt-get update`` was executed on the system.

        .. note::

            This parameter is available only on Debian based distributions and
            has no effect on the rest.

    :param str fromrepo:
        Specify a repository from which to install

        .. note::

            Distros which use APT (Debian, Ubuntu, etc.) do not have a concept
            of repositories, in the same way as YUM-based distros do. When a
            source is added, it is assigned to a given release. Consider the
            following source configuration:

            .. code-block:: text

                deb http://ppa.launchpad.net/saltstack/salt/ubuntu precise main

            The packages provided by this source would be made available via
            the ``precise`` release, therefore ``fromrepo`` would need to be
            set to ``precise`` for Salt to install the package from this
            source.

            Having multiple sources in the same release may result in the
            default install candidate being newer than what is desired. If this
            is the case, the desired version must be specified using the
            ``version`` parameter.

            If the ``pkgs`` parameter is being used to install multiple
            packages in the same state, then instead of using ``version``,
            use the method of version specification described in the **Multiple
            Package Installation Options** section below.

            Running the shell command ``apt-cache policy pkgname`` on a minion
            can help elucidate the APT configuration and aid in properly
            configuring states:

            .. code-block:: bash

                root@saltmaster:~# salt ubuntu01 cmd.run 'apt-cache policy ffmpeg'
                ubuntu01:
                    ffmpeg:
                    Installed: (none)
                    Candidate: 7:0.10.11-1~precise1
                    Version table:
                        7:0.10.11-1~precise1 0
                            500 http://ppa.launchpad.net/jon-severinsson/ffmpeg/ubuntu/ precise/main amd64 Packages
                        4:0.8.10-0ubuntu0.12.04.1 0
                            500 http://us.archive.ubuntu.com/ubuntu/ precise-updates/main amd64 Packages
                            500 http://security.ubuntu.com/ubuntu/ precise-security/main amd64 Packages
                        4:0.8.1-0ubuntu1 0
                            500 http://us.archive.ubuntu.com/ubuntu/ precise/main amd64 Packages

            The release is located directly after the source's URL. The actual
            release name is the part before the slash, so to install version
            **4:0.8.10-0ubuntu0.12.04.1** either ``precise-updates`` or
            ``precise-security`` could be used for the ``fromrepo`` value.

    :param bool skip_verify:
        Skip the GPG verification check for the package to be installed

    :param bool skip_suggestions:
        Force strict package naming. Disables lookup of package alternatives.

        .. versionadded:: 2014.1.1

    :param bool allow_updates:
        Allow the package to be updated outside Salt's control (e.g. auto
        updates on Windows). This means a package on the Minion can have a
        newer version than the latest available in the repository without
        enforcing a re-installation of the package.

        .. versionadded:: 2014.7.0

        Example:

        .. code-block:: yaml

            httpd:
              pkg.installed:
                - fromrepo: mycustomrepo
                - skip_verify: True
                - skip_suggestions: True
                - version: 2.0.6~ubuntu3
                - refresh: True
                - allow_updates: True
                - hold: False

    :param bool pkg_verify:

        .. versionadded:: 2014.7.0

        For requested packages that are already installed and would not be
        targeted for upgrade or downgrade, use pkg.verify to determine if any
        of the files installed by the package have been altered. If files have
        been altered, the reinstall option of pkg.install is used to force a
        reinstall. Types to ignore can be passed to pkg.verify. Additionally,
        ``verify_options`` can be used to modify further the behavior of
        pkg.verify. See examples below.  Currently, this option is supported
        for the following pkg providers: :mod:`yumpkg <salt.modules.yumpkg>`.

        Examples:

        .. code-block:: yaml

            httpd:
              pkg.installed:
                - version: 2.2.15-30.el6.centos
                - pkg_verify: True

        .. code-block:: yaml

            mypkgs:
              pkg.installed:
                - pkgs:
                  - foo
                  - bar: 1.2.3-4
                  - baz
                - pkg_verify:
                  - ignore_types:
                    - config
                    - doc

        .. code-block:: yaml

            mypkgs:
              pkg.installed:
                - pkgs:
                  - foo
                  - bar: 1.2.3-4
                  - baz
                - pkg_verify:
                  - ignore_types:
                    - config
                    - doc
                  - verify_options:
                    - nodeps
                    - nofiledigest

    :param list ignore_types:
        List of types to ignore when verifying the package

        .. versionadded:: 2014.7.0

    :param list verify_options:
        List of additional options to pass when verifying the package. These
        options will be added to the ``rpm -V`` command, prepended with ``--``
        (for example, when ``nodeps`` is passed in this option, ``rpm -V`` will
        be run with ``--nodeps``).

        .. versionadded:: 2016.11.0

    :param bool normalize:
        Normalize the package name by removing the architecture, if the
        architecture of the package is different from the architecture of the
        operating system. The ability to disable this behavior is useful for
        poorly-created packages which include the architecture as an actual
        part of the name, such as kernel modules which match a specific kernel
        version.

        .. versionadded:: 2014.7.0

        Example:

        .. code-block:: yaml

            gpfs.gplbin-2.6.32-279.31.1.el6.x86_64:
              pkg.installed:
                - normalize: False

    :param bool ignore_epoch:
        When a package version contains an non-zero epoch (e.g.
        ``1:3.14.159-2.el7``, and a specific version of a package is desired,
        set this option to ``True`` to ignore the epoch when comparing
        versions. This allows for the following SLS to be used:

        .. code-block:: yaml

            # Actual vim-enhanced version: 2:7.4.160-1.el7
            vim-enhanced:
              pkg.installed:
                - version: 7.4.160-1.el7
                - ignore_epoch: True

        Without this option set to ``True`` in the above example, the package
        would be installed, but the state would report as failed because the
        actual installed version would be ``2:7.4.160-1.el7``. Alternatively,
        this option can be left as ``False`` and the full version string (with
        epoch) can be specified in the SLS file:

        .. code-block:: yaml

            vim-enhanced:
              pkg.installed:
                - version: 2:7.4.160-1.el7

        .. versionadded:: 2015.8.9

    |

    **MULTIPLE PACKAGE INSTALLATION OPTIONS: (not supported in pkgng)**

    :param list pkgs:
        A list of packages to install from a software repository. All packages
        listed under ``pkgs`` will be installed via a single command.

        .. code-block:: yaml

            mypkgs:
              pkg.installed:
                - pkgs:
                  - foo
                  - bar
                  - baz
                - hold: True

        ``NOTE:`` For :mod:`apt <salt.modules.aptpkg>`,
        :mod:`ebuild <salt.modules.ebuild>`,
        :mod:`pacman <salt.modules.pacman>`, :mod:`yumpkg <salt.modules.yumpkg>`,
        and :mod:`zypper <salt.modules.zypper>`, version numbers can be specified
        in the ``pkgs`` argument. For example:

        .. code-block:: yaml

            mypkgs:
              pkg.installed:
                - pkgs:
                  - foo
                  - bar: 1.2.3-4
                  - baz

        Additionally, :mod:`ebuild <salt.modules.ebuild>`, :mod:`pacman
        <salt.modules.pacman>` and :mod:`zypper <salt.modules.zypper>` support
        the ``<``, ``<=``, ``>=``, and ``>`` operators for more control over
        what versions will be installed. For example:

        .. code-block:: yaml

            mypkgs:
              pkg.installed:
                - pkgs:
                  - foo
                  - bar: '>=1.2.3-4'
                  - baz

        ``NOTE:`` When using comparison operators, the expression must be enclosed
        in quotes to avoid a YAML render error.

        With :mod:`ebuild <salt.modules.ebuild>` is also possible to specify a
        use flag list and/or if the given packages should be in
        package.accept_keywords file and/or the overlay from which you want the
        package to be installed. For example:

        .. code-block:: yaml

            mypkgs:
              pkg.installed:
                - pkgs:
                  - foo: '~'
                  - bar: '~>=1.2:slot::overlay[use,-otheruse]'
                  - baz

    :param list sources:
        A list of packages to install, along with the source URI or local path
        from which to install each package. In the example below, ``foo``,
        ``bar``, ``baz``, etc. refer to the name of the package, as it would
        appear in the output of the ``pkg.version`` or ``pkg.list_pkgs`` salt
        CLI commands.

        .. code-block:: yaml

            mypkgs:
              pkg.installed:
                - sources:
                  - foo: salt://rpms/foo.rpm
                  - bar: http://somesite.org/bar.rpm
                  - baz: ftp://someothersite.org/baz.rpm
                  - qux: /minion/path/to/qux.rpm

    **PLATFORM-SPECIFIC ARGUMENTS**

    These are specific to each OS. If it does not apply to the execution
    module for your OS, it is ignored.

    :param bool hold:
        Force the package to be held at the current installed version.
        Currently works with YUM/DNF & APT based systems.

        .. versionadded:: 2014.7.0

    :param bool update_holds:
        If ``True``, and this function would update the package version, any
        packages which are being held will be temporarily unheld so that they
        can be updated. Otherwise, if this function attempts to update a held
        package, the held package(s) will be skipped and the state will fail.
        By default, this parameter is set to ``False``.

        Currently works with YUM/DNF & APT based systems.

        .. versionadded:: 2016.11.0

    :param list names:
        A list of packages to install from a software repository. Each package
        will be installed individually by the package manager.

        .. warning::

            Unlike ``pkgs``, the ``names`` parameter cannot specify a version.
            In addition, it makes a separate call to the package management
            frontend to install each package, whereas ``pkgs`` makes just a
            single call. It is therefore recommended to use ``pkgs`` instead of
            ``names`` to install multiple packages, both for the additional
            features and the performance improvement that it brings.

    :param bool install_recommends:
        Whether to install the packages marked as recommended. Default is
        ``True``. Currently only works with APT-based systems.

        .. versionadded:: 2015.5.0

        .. code-block:: yaml

            httpd:
              pkg.installed:
                - install_recommends: False

    :param bool only_upgrade:
        Only upgrade the packages, if they are already installed. Default is
        ``False``. Currently only works with APT-based systems.

        .. versionadded:: 2015.5.0

        .. code-block:: yaml

            httpd:
              pkg.installed:
                - only_upgrade: True

        .. note::
            If this parameter is set to True and the package is not already
            installed, the state will fail.

   :param bool report_reboot_exit_codes:
       If the installer exits with a recognized exit code indicating that
       a reboot is required, the module function

           *win_system.set_reboot_required_witnessed*

       will be called, preserving the knowledge of this event
       for the remainder of the current boot session. For the time being,
       ``3010`` is the only recognized exit code,
       but this is subject to future refinement.
       The value of this param
       defaults to ``True``. This parameter has no effect
       on non-Windows systems.

       .. versionadded:: 2016.11.0

       .. code-block:: yaml

           ms vcpp installed:
             pkg.installed:
               - name: ms-vcpp
               - version: 10.0.40219
               - report_reboot_exit_codes: False

    :return:
        A dictionary containing the state of the software installation
    :rtype dict:

    .. note::

        The ``pkg.installed`` state supports the usage of ``reload_modules``.
        This functionality allows you to force Salt to reload all modules. In
        many cases, Salt is clever enough to transparently reload the modules.
        For example, if you install a package, Salt reloads modules because some
        other module or state might require the package which was installed.
        However, there are some edge cases where this may not be the case, which
        is what ``reload_modules`` is meant to resolve.

        You should only use ``reload_modules`` if your ``pkg.installed`` does some
        sort of installation where if you do not reload the modules future items
        in your state which rely on the software being installed will fail. Please
        see the :ref:`Reloading Modules <reloading-modules>` documentation for more
        information.

    '''
    if isinstance(pkgs, list) and len(pkgs) == 0:
        return {'name': name,
                'changes': {},
                'result': True,
                'comment': 'No packages to install provided'}

    kwargs['saltenv'] = __env__
    refresh = salt.utils.pkg.check_refresh(__opts__, refresh)
    if not isinstance(pkg_verify, list):
        pkg_verify = pkg_verify is True
    if (pkg_verify or isinstance(pkg_verify, list)) \
            and 'pkg.verify' not in __salt__:
        return {'name': name,
                'changes': {},
                'result': False,
                'comment': 'pkg.verify not implemented'}

    if not isinstance(version, six.string_types) and version is not None:
        version = str(version)

    kwargs['allow_updates'] = allow_updates

    result = _find_install_targets(name, version, pkgs, sources,
                                   fromrepo=fromrepo,
                                   skip_suggestions=skip_suggestions,
                                   pkg_verify=pkg_verify,
                                   normalize=normalize,
                                   ignore_epoch=ignore_epoch,
                                   reinstall=reinstall,
                                   refresh=refresh,
                                   **kwargs)

    try:
        (desired, targets, to_unpurge, to_reinstall,
         altered_files, warnings, was_refreshed) = result
        if was_refreshed:
            refresh = False
    except ValueError:
        # _find_install_targets() found no targets or encountered an error

        # check that the hold function is available
        if 'pkg.hold' in __salt__:
            if 'hold' in kwargs:
                try:
                    if kwargs['hold']:
                        hold_ret = __salt__['pkg.hold'](
                            name=name, pkgs=pkgs, sources=sources
                        )
                    else:
                        hold_ret = __salt__['pkg.unhold'](
                            name=name, pkgs=pkgs, sources=sources
                        )
                except (CommandExecutionError, SaltInvocationError) as exc:
                    return {'name': name,
                            'changes': {},
                            'result': False,
                            'comment': str(exc)}

                if 'result' in hold_ret and not hold_ret['result']:
                    return {'name': name,
                            'changes': {},
                            'result': False,
                            'comment': 'An error was encountered while '
                                       'holding/unholding package(s): {0}'
                                       .format(hold_ret['comment'])}
                else:
                    modified_hold = [hold_ret[x] for x in hold_ret
                                     if hold_ret[x]['changes']]
                    not_modified_hold = [hold_ret[x] for x in hold_ret
                                         if not hold_ret[x]['changes']
                                         and hold_ret[x]['result']]
                    failed_hold = [hold_ret[x] for x in hold_ret
                                   if not hold_ret[x]['result']]

                    if modified_hold:
                        for i in modified_hold:
                            result['comment'] += '.\n{0}'.format(i['comment'])
                            result['result'] = i['result']
                            result['changes'][i['name']] = i['changes']

                    if not_modified_hold:
                        for i in not_modified_hold:
                            result['comment'] += '.\n{0}'.format(i['comment'])
                            result['result'] = i['result']

                    if failed_hold:
                        for i in failed_hold:
                            result['comment'] += '.\n{0}'.format(i['comment'])
                            result['result'] = i['result']
        return result

    if to_unpurge and 'lowpkg.unpurge' not in __salt__:
        ret = {'name': name,
               'changes': {},
               'result': False,
               'comment': 'lowpkg.unpurge not implemented'}
        if warnings:
            ret['comment'] += '.' + '. '.join(warnings) + '.'
        return ret

    # Remove any targets not returned by _find_install_targets
    if pkgs:
        pkgs = [dict([(x, y)]) for x, y in six.iteritems(targets)]
        pkgs.extend([dict([(x, y)]) for x, y in six.iteritems(to_reinstall)])
    elif sources:
        oldsources = sources
        sources = [x for x in oldsources
                   if next(iter(list(x.keys()))) in targets]
        sources.extend([x for x in oldsources
                        if next(iter(list(x.keys()))) in to_reinstall])

    comment = []
    if __opts__['test']:
        if targets:
            if sources:
                summary = ', '.join(targets)
            else:
                summary = ', '.join([_get_desired_pkg(x, targets)
                                     for x in targets])
            comment.append('The following packages would be '
                           'installed/updated: {0}'.format(summary))
        if to_unpurge:
            comment.append(
                'The following packages would have their selection status '
                'changed from \'purge\' to \'install\': {0}'
                .format(', '.join(to_unpurge))
            )
        if to_reinstall:
            # Add a comment for each package in to_reinstall with its
            # pkg.verify output
            if reinstall:
                reinstall_targets = []
                for reinstall_pkg in to_reinstall:
                    if sources:
                        reinstall_targets.append(reinstall_pkg)
                    else:
                        reinstall_targets.append(
                            _get_desired_pkg(reinstall_pkg, to_reinstall)
                        )
                msg = 'The following packages would be reinstalled: '
                msg += ', '.join(reinstall_targets)
                comment.append(msg)
            else:
                for reinstall_pkg in to_reinstall:
                    if sources:
                        pkgstr = reinstall_pkg
                    else:
                        pkgstr = _get_desired_pkg(reinstall_pkg, to_reinstall)
                    comment.append(
                        'Package \'{0}\' would be reinstalled because the '
                        'following files have been altered:'.format(pkgstr)
                    )
                    comment.append(
                        _nested_output(altered_files[reinstall_pkg])
                    )
        ret = {'name': name,
               'changes': {},
               'result': None,
               'comment': '\n'.join(comment)}
        if warnings:
            ret['comment'] += '\n' + '. '.join(warnings) + '.'
        return ret

    changes = {'installed': {}}
    modified_hold = None
    not_modified_hold = None
    failed_hold = None
    if targets or to_reinstall:
        force = False
        if salt.utils.is_freebsd():
            force = True    # Downgrades need to be forced.
        try:
            pkg_ret = __salt__['pkg.install'](name,
                                              refresh=refresh,
                                              version=version,
                                              force=force,
                                              fromrepo=fromrepo,
                                              skip_verify=skip_verify,
                                              pkgs=pkgs,
                                              sources=sources,
                                              reinstall=bool(to_reinstall),
                                              normalize=normalize,
                                              update_holds=update_holds,
                                              **kwargs)
        except CommandExecutionError as exc:
            ret = {'name': name, 'result': False}
            if exc.info:
                # Get information for state return from the exception.
                ret['changes'] = exc.info.get('changes', {})
                ret['comment'] = exc.strerror_without_changes
            else:
                ret['changes'] = {}
                ret['comment'] = ('An error was encountered while installing '
                                  'package(s): {0}'.format(exc))
            if warnings:
                ret['comment'] += '\n\n' + '. '.join(warnings) + '.'
            return ret

        if refresh:
            refresh = False

        if isinstance(pkg_ret, dict):
            changes['installed'].update(pkg_ret)
        elif isinstance(pkg_ret, six.string_types):
            comment.append(pkg_ret)
            # Code below will be looking for a dictionary. If this is a string
            # it means that there was an exception raised and that no packages
            # changed, so now that we have added this error to the comments we
            # set this to an empty dictionary so that the code below which
            # checks reinstall targets works.
            pkg_ret = {}

        if 'pkg.hold' in __salt__:
            if 'hold' in kwargs:
                try:
                    if kwargs['hold']:
                        hold_ret = __salt__['pkg.hold'](
                            name=name, pkgs=pkgs, sources=sources
                        )
                    else:
                        hold_ret = __salt__['pkg.unhold'](
                            name=name, pkgs=pkgs, sources=sources
                        )
                except (CommandExecutionError, SaltInvocationError) as exc:
                    comment.append(str(exc))
                    ret = {'name': name,
                           'changes': changes,
                           'result': False,
                           'comment': '\n'.join(comment)}
                    if warnings:
                        ret['comment'] += '.' + '. '.join(warnings) + '.'
                    return ret
                else:
                    if 'result' in hold_ret and not hold_ret['result']:
                        ret = {'name': name,
                               'changes': {},
                               'result': False,
                               'comment': 'An error was encountered while '
                                          'holding/unholding package(s): {0}'
                                          .format(hold_ret['comment'])}
                        if warnings:
                            ret['comment'] += '.' + '. '.join(warnings) + '.'
                        return ret
                    else:
                        modified_hold = [hold_ret[x] for x in hold_ret
                                         if hold_ret[x]['changes']]
                        not_modified_hold = [hold_ret[x] for x in hold_ret
                                             if not hold_ret[x]['changes']
                                             and hold_ret[x]['result']]
                        failed_hold = [hold_ret[x] for x in hold_ret
                                       if not hold_ret[x]['result']]

    if to_unpurge:
        changes['purge_desired'] = __salt__['lowpkg.unpurge'](*to_unpurge)

    # Analyze pkg.install results for packages in targets
    if sources:
        modified = [x for x in changes['installed'] if x in targets]
        not_modified = [x for x in desired
                        if x not in targets
                        and x not in to_reinstall]
        failed = [x for x in targets if x not in modified]
    else:
        if __grains__['os'] == 'FreeBSD':
            kwargs['with_origin'] = True
        new_pkgs = __salt__['pkg.list_pkgs'](versions_as_list=True, **kwargs)
        ok, failed = _verify_install(desired, new_pkgs,
                                     ignore_epoch=ignore_epoch)
        modified = [x for x in ok if x in targets]
        not_modified = [x for x in ok
                        if x not in targets
                        and x not in to_reinstall]
        failed = [x for x in failed if x in targets]

    # If there was nothing unpurged, just set the changes dict to the contents
    # of changes['installed'].
    if not changes.get('purge_desired'):
        changes = changes['installed']

    if modified:
        if sources:
            summary = ', '.join(modified)
        else:
            summary = ', '.join([_get_desired_pkg(x, desired)
                                 for x in modified])
        if len(summary) < 20:
            comment.append('The following packages were installed/updated: '
                           '{0}'.format(summary))
        else:
            comment.append(
                '{0} targeted package{1} {2} installed/updated.'.format(
                    len(modified),
                    's' if len(modified) > 1 else '',
                    'were' if len(modified) > 1 else 'was'
                )
            )

    if modified_hold:
        for i in modified_hold:
            change_name = i['name']
            if change_name in changes:
                comment.append(i['comment'])
                if len(changes[change_name]['new']) > 0:
                    changes[change_name]['new'] += '\n'
                changes[change_name]['new'] += '{0}'.format(i['changes']['new'])
                if len(changes[change_name]['old']) > 0:
                    changes[change_name]['old'] += '\n'
                changes[change_name]['old'] += '{0}'.format(i['changes']['old'])

    # Any requested packages that were not targeted for install or reinstall
    if not_modified:
        if sources:
            summary = ', '.join(not_modified)
        else:
            summary = ', '.join([_get_desired_pkg(x, desired)
                                 for x in not_modified])
        if len(not_modified) <= 20:
            comment.append('The following packages were already installed: '
                           '{0}'.format(summary))
        else:
            comment.append(
                '{0} targeted package{1} {2} already installed'.format(
                    len(not_modified),
                    's' if len(not_modified) > 1 else '',
                    'were' if len(not_modified) > 1 else 'was'
                )
            )

    if not_modified_hold:
        for i in not_modified_hold:
            comment.append(i['comment'])

    result = True

    if failed:
        if sources:
            summary = ', '.join(failed)
        else:
            summary = ', '.join([_get_desired_pkg(x, desired)
                                 for x in failed])
        comment.insert(0, 'The following packages failed to '
                          'install/update: {0}'.format(summary))
        result = False

    if failed_hold:
        for i in failed_hold:
            comment.append(i['comment'])
        result = False

    # Get the ignore_types list if any from the pkg_verify argument
    if isinstance(pkg_verify, list) \
            and any(x.get('ignore_types') is not None
                    for x in pkg_verify
                    if isinstance(x, _OrderedDict)
                    and 'ignore_types' in x):
        ignore_types = next(x.get('ignore_types')
                            for x in pkg_verify
                            if 'ignore_types' in x)
    else:
        ignore_types = []

    # Get the verify_options list if any from the pkg_verify argument
    if isinstance(pkg_verify, list) \
            and any(x.get('verify_options') is not None
                    for x in pkg_verify
                    if isinstance(x, _OrderedDict)
                    and 'verify_options' in x):
        verify_options = next(x.get('verify_options')
                            for x in pkg_verify
                            if 'verify_options' in x)
    else:
        verify_options = []

    # Rerun pkg.verify for packages in to_reinstall to determine failed
    modified = []
    failed = []
    for reinstall_pkg in to_reinstall:
        if reinstall:
            if reinstall_pkg in pkg_ret:
                modified.append(reinstall_pkg)
            else:
                failed.append(reinstall_pkg)
        elif pkg_verify:
            # No need to wrap this in a try/except because we would already
            # have caught invalid arguments earlier.
            verify_result = __salt__['pkg.verify'](reinstall_pkg,
                                                   ignore_types=ignore_types,
                                                   verify_options=verify_options)
            if verify_result:
                failed.append(reinstall_pkg)
                altered_files[reinstall_pkg] = verify_result
            else:
                modified.append(reinstall_pkg)

    if modified:
        # Add a comment for each package in modified with its pkg.verify output
        for modified_pkg in modified:
            if sources:
                pkgstr = modified_pkg
            else:
                pkgstr = _get_desired_pkg(modified_pkg, desired)
            msg = 'Package {0} was reinstalled.'.format(pkgstr)
            if modified_pkg in altered_files:
                msg += ' The following files were remediated:'
                comment.append(msg)
                comment.append(_nested_output(altered_files[modified_pkg]))
            else:
                comment.append(msg)

    if failed:
        # Add a comment for each package in failed with its pkg.verify output
        for failed_pkg in failed:
            if sources:
                pkgstr = failed_pkg
            else:
                pkgstr = _get_desired_pkg(failed_pkg, desired)
            msg = ('Reinstall was not successful for package {0}.'
                   .format(pkgstr))
            if failed_pkg in altered_files:
                msg += ' The following files could not be remediated:'
                comment.append(msg)
                comment.append(_nested_output(altered_files[failed_pkg]))
            else:
                comment.append(msg)
        result = False

    ret = {'name': name,
           'changes': changes,
           'result': result,
           'comment': '\n'.join(comment)}
    if warnings:
        ret['comment'] += '\n' + '. '.join(warnings) + '.'
    return ret