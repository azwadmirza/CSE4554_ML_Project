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
    ret = {}

    # Make sure name or pkgs is passed
    if not name and not pkgs:
        return 'Must pass a single package or a list of packages'

    # Get package parameters
    pkg_params = __salt__['pkg_resource.parse_targets'](name, pkgs, **kwargs)[0]

    # Get a list of currently installed software for comparison at the end
    old = list_pkgs()

    # Loop through each package
    changed = []
    for target in pkg_params:

        # Load package information for the package
        pkginfo = _get_package_info(target)

        # Make sure pkginfo was found
        if not pkginfo:
            log.error('Unable to locate package {0}'.format(name))
            ret[target] = 'Unable to locate package {0}'.format(target)
            continue

        # Get latest version if no version passed, else use passed version
        if not version:
            version_num = _get_latest_pkg_version(pkginfo)
        else:
            version_num = version

        if 'latest' in pkginfo and version_num not in pkginfo:
            version_num = 'latest'

        # Check to see if package is installed on the system
        if target not in old:
            log.error('{0} {1} not installed'.format(target, version))
            ret[target] = {'current': 'not installed'}
            continue
        else:
            if not version_num == old.get(target) \
                    and not old.get(target) == "Not Found" \
                    and version_num != 'latest':
                log.error('{0} {1} not installed'.format(target, version))
                ret[target] = {'current': '{0} not installed'.format(version_num)}
                continue

        # Get the uninstaller
        uninstaller = pkginfo[version_num].get('uninstaller')

        # If no uninstaller found, use the installer
        if not uninstaller:
            uninstaller = pkginfo[version_num].get('installer')

        # If still no uninstaller found, fail
        if not uninstaller:
            log.error('Error: No installer or uninstaller configured for package {0}'.format(name))
            ret[target] = {'no uninstaller': version_num}
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
                    log.error('Unable to cache {0}'.format(uninstaller))
                    ret[target] = {'unable to cache': uninstaller}
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
        uninstall_flags = '{0}'.format(pkginfo[version_num].get('uninstall_flags', ''))
        if kwargs.get('extra_uninstall_flags'):
            uninstall_flags = '{0} {1}'.format(uninstall_flags,
                                               kwargs.get('extra_uninstall_flags', ""))

        # Uninstall the software
        # Check Use Scheduler Option
        if pkginfo[version_num].get('use_scheduler', False):

            # Build Scheduled Task Parameters
            if pkginfo[version_num].get('msiexec'):
                cmd = 'msiexec.exe'
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
                                         start_time='01:00')
            # Run Scheduled Task
            __salt__['task.run_wait'](name='update-salt-software')
        else:
            # Build the install command
            cmd = []
            if pkginfo[version_num].get('msiexec'):
                cmd.extend(['msiexec', '/x', expanded_cached_pkg])
            else:
                cmd.append(expanded_cached_pkg)
            cmd.extend(salt.utils.shlex_split(uninstall_flags))
            # Launch the command
            result = __salt__['cmd.run_stdout'](cmd,
                                                output_loglevel='trace',
                                                python_shell=False)
            if result:
                log.error('Failed to install {0}'.format(target))
                log.error('error message: {0}'.format(result))
                ret[target] = {'failed': result}
            else:
                changed.append(target)

    # Get a new list of installed software
    new = list_pkgs()
    tries = 0
    difference = salt.utils.compare_dicts(old, new)

    while not all(name in difference for name in changed) and tries <= 1000:
        new = list_pkgs()
        difference = salt.utils.compare_dicts(old, new)
        tries += 1
        if tries == 1000:
            ret['_comment'] = 'Registry not updated.'

    # Compare the software list before and after
    # Add the difference to ret
    ret.update(difference)

    return ret