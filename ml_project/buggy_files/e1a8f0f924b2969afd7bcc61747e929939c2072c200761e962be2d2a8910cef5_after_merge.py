def remove(name=None, pkgs=None, version=None, **kwargs):
    '''
    Remove the passed package(s) from the system using winrepo

    :param name:
        The name of the package to be uninstalled.
    :type name: str, list, or None

    :param str version:
        The version of the package to be uninstalled. If this option is used to
        to uninstall multiple packages, then this version will be applied to all
        targeted packages. Recommended using only when uninstalling a single
        package. If this parameter is omitted, the latest version will be
        uninstalled.

    Multiple Package Options:

    :param pkgs:
        A list of packages to delete. Must be passed as a python list. The
        ``name`` parameter will be ignored if this option is passed.
    :type pkgs: list or None

    .. versionadded:: 0.16.0

    *Keyword Arguments (kwargs)*
    :param str saltenv: Salt environment. Default ``base``
    :param bool refresh: Refresh package metadata. Default ``False``

    :return: Returns a dict containing the changes.
    :rtype: dict

        If the package is removed by ``pkg.remove``:

            {'<package>': {'old': '<old-version>',
                           'new': '<new-version>'}}

        If the package is already uninstalled:

            {'<package>': {'current': 'not installed'}}

    CLI Example:

    .. code-block:: bash

        salt '*' pkg.remove <package name>
        salt '*' pkg.remove <package1>,<package2>,<package3>
        salt '*' pkg.remove pkgs='["foo", "bar"]'
    '''
    saltenv = kwargs.get('saltenv', 'base')
    refresh = salt.utils.is_true(kwargs.get('refresh', False))
    # no need to call _refresh_db_conditional as list_pkgs will do it
    ret = {}

    # Make sure name or pkgs is passed
    if not name and not pkgs:
        return 'Must pass a single package or a list of packages'

    # Get package parameters
    pkg_params = __salt__['pkg_resource.parse_targets'](name, pkgs, **kwargs)[0]

    # Get a list of currently installed software for comparison at the end
    old = list_pkgs(saltenv=saltenv, refresh=refresh, versions_as_list=True)

    # Loop through each package
    changed = []
    for pkgname, version_num in six.iteritems(pkg_params):

        # Load package information for the package
        pkginfo = _get_package_info(pkgname, saltenv=saltenv)

        # Make sure pkginfo was found
        if not pkginfo:
            msg = 'Unable to locate package {0}'.format(pkgname)
            log.error(msg)
            ret[pkgname] = msg
            continue

        if version_num is not None:
            if version_num not in pkginfo and 'latest' in pkginfo:
                version_num = 'latest'
        elif 'latest' in pkginfo:
            version_num = 'latest'

        # Check to see if package is installed on the system
        removal_targets = []
        if pkgname not in old:
            log.error('%s %s not installed', pkgname, version)
            ret[pkgname] = {'current': 'not installed'}
            continue
        else:
            if version_num is None:
                removal_targets.extend(old[pkgname])
            elif version_num not in old[pkgname] \
                    and 'Not Found' not in old[pkgname] \
                    and version_num != 'latest':
                log.error('%s %s not installed', pkgname, version)
                ret[pkgname] = {
                    'current': '{0} not installed'.format(version_num)
                }
                continue
            else:
                removal_targets.append(version_num)

        for target in removal_targets:
            # Get the uninstaller
            uninstaller = pkginfo[target].get('uninstaller')

            # If no uninstaller found, use the installer
            if not uninstaller:
                uninstaller = pkginfo[target].get('installer')

            # If still no uninstaller found, fail
            if not uninstaller:
                log.error(
                    'No installer or uninstaller configured for package %s',
                    pkgname,
                )
                ret[pkgname] = {'no uninstaller': target}
                continue

            # Where is the uninstaller
            if uninstaller.startswith(('salt:', 'http:', 'https:', 'ftp:')):

                # Check to see if the uninstaller is cached
                cached_pkg = __salt__['cp.is_cached'](uninstaller)
                if not cached_pkg:
                    # It's not cached. Cache it, mate.
                    cached_pkg = __salt__['cp.cache_file'](uninstaller)

                    # Check if the uninstaller was cached successfully
                    if not cached_pkg:
                        log.error('Unable to cache %s', uninstaller)
                        ret[pkgname] = {'unable to cache': uninstaller}
                        continue
            else:
                # Run the uninstaller directly (not hosted on salt:, https:, etc.)
                cached_pkg = uninstaller

            # Fix non-windows slashes
            cached_pkg = cached_pkg.replace('/', '\\')
            cache_path, _ = os.path.split(cached_pkg)

            # Get parameters for cmd
            expanded_cached_pkg = str(os.path.expandvars(cached_pkg))

            # Get uninstall flags
            uninstall_flags = '{0}'.format(
                pkginfo[target].get('uninstall_flags', '')
            )
            if kwargs.get('extra_uninstall_flags'):
                uninstall_flags = '{0} {1}'.format(
                    uninstall_flags,
                    kwargs.get('extra_uninstall_flags', "")
                )

            #Compute msiexec string
            use_msiexec, msiexec = _get_msiexec(pkginfo[target].get('msiexec', False))

            # Uninstall the software
            # Check Use Scheduler Option
            if pkginfo[target].get('use_scheduler', False):

                # Build Scheduled Task Parameters
                if use_msiexec:
                    cmd = msiexec
                    arguments = ['/x']
                    arguments.extend(salt.utils.shlex_split(uninstall_flags))
                else:
                    cmd = expanded_cached_pkg
                    arguments = salt.utils.shlex_split(uninstall_flags)

                # Create Scheduled Task
                __salt__['task.create_task'](name='update-salt-software',
                                             user_name='System',
                                             force=True,
                                             action_type='Execute',
                                             cmd=cmd,
                                             arguments=' '.join(arguments),
                                             start_in=cache_path,
                                             trigger_type='Once',
                                             start_date='1975-01-01',
                                             start_time='01:00',
                                             ac_only=False,
                                             stop_if_on_batteries=False)
                # Run Scheduled Task
                if not __salt__['task.run_wait'](name='update-salt-software'):
                    log.error('Failed to remove %s', pkgname)
                    log.error('Scheduled Task failed to run')
                    ret[pkgname] = {'uninstall status': 'failed'}
            else:
                # Build the install command
                cmd = []
                if use_msiexec:
                    cmd.extend([msiexec, '/x', expanded_cached_pkg])
                else:
                    cmd.append(expanded_cached_pkg)
                cmd.extend(salt.utils.shlex_split(uninstall_flags))
                # Launch the command
                result = __salt__['cmd.run_all'](cmd,
                                                 output_loglevel='trace',
                                                 python_shell=False,
                                                 redirect_stderr=True)
                if not result['retcode']:
                    ret[pkgname] = {'uninstall status': 'success'}
                    changed.append(pkgname)
                else:
                    log.error('Failed to remove %s', pkgname)
                    log.error('retcode %s', result['retcode'])
                    log.error('uninstaller output: %s', result['stdout'])
                    ret[pkgname] = {'uninstall status': 'failed'}

    # Get a new list of installed software
    new = list_pkgs(saltenv=saltenv)

    # Take the "old" package list and convert the values to strings in
    # preparation for the comparison below.
    __salt__['pkg_resource.stringify'](old)

    difference = salt.utils.compare_dicts(old, new)
    tries = 0
    while not all(name in difference for name in changed) and tries <= 1000:
        new = list_pkgs(saltenv=saltenv)
        difference = salt.utils.compare_dicts(old, new)
        tries += 1
        if tries == 1000:
            ret['_comment'] = 'Registry not updated.'

    # Compare the software list before and after
    # Add the difference to ret
    ret.update(difference)

    return ret