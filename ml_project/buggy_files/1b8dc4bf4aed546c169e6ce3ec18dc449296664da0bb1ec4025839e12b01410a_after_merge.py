def install(name=None, refresh=False, pkgs=None, **kwargs):
    r'''
    Install the passed package(s) on the system using winrepo

    Args:

        name (str):
            The name of a single package, or a comma-separated list of packages
            to install. (no spaces after the commas)

        refresh (bool):
            Boolean value representing whether or not to refresh the winrepo db

        pkgs (list):
            A list of packages to install from a software repository. All
            packages listed under ``pkgs`` will be installed via a single
            command.

            You can specify a version by passing the item as a dict:

            CLI Example:

            .. code-block:: bash

                # will install the latest version of foo and bar
                salt '*' pkg.install pkgs='["foo", "bar"]'

                # will install the latest version of foo and version 1.2.3 of bar
                salt '*' pkg.install pkgs='["foo", {"bar": "1.2.3"}]'

    Kwargs:

        version (str):
            The specific version to install. If omitted, the latest version will
            be installed. Recommend for use when installing a single package.

            If passed with a list of packages in the ``pkgs`` parameter, the
            version will be ignored.

            CLI Example:

             .. code-block:: bash

                # Version is ignored
                salt '*' pkg.install pkgs="['foo', 'bar']" version=1.2.3

            If passed with a comma seperated list in the ``name`` parameter, the
            version will apply to all packages in the list.

            CLI Example:

             .. code-block:: bash

                # Version 1.2.3 will apply to packages foo and bar
                salt '*' pkg.install foo,bar version=1.2.3

        cache_file (str):
            A single file to copy down for use with the installer. Copied to the
            same location as the installer. Use this over ``cache_dir`` if there
            are many files in the directory and you only need a specific file
            and don't want to cache additional files that may reside in the
            installer directory. Only applies to files on ``salt://``

        cache_dir (bool):
            True will copy the contents of the installer directory. This is
            useful for installations that are not a single file. Only applies to
            directories on ``salt://``

        extra_install_flags (str):
            Additional install flags that will be appended to the
            ``install_flags`` defined in the software definition file. Only
            applies when single package is passed.

        saltenv (str):
            Salt environment. Default 'base'

        report_reboot_exit_codes (bool):
            If the installer exits with a recognized exit code indicating that
            a reboot is required, the module function

           *win_system.set_reboot_required_witnessed*

            will be called, preserving the knowledge of this event
            for the remainder of the current boot session. For the time being,
            3010 is the only recognized exit code. The value of this param
            defaults to True.

            .. versionadded:: 2016.11.0

    Returns:
        dict: Return a dict containing the new package names and versions:

        If the package is installed by ``pkg.install``:

        .. code-block:: cfg

            {'<package>': {'old': '<old-version>',
                           'new': '<new-version>'}}

        If the package is already installed:

        .. code-block:: cfg

            {'<package>': {'current': '<current-version>'}}

    The following example will refresh the winrepo and install a single package,
    7zip.

    CLI Example:

    .. code-block:: bash

        salt '*' pkg.install 7zip refresh=True

    CLI Example:

    .. code-block:: bash

        salt '*' pkg.install 7zip
        salt '*' pkg.install 7zip,filezilla
        salt '*' pkg.install pkgs='["7zip","filezilla"]'

    WinRepo Definition File Examples:

    The following example demonstrates the use of ``cache_file``. This would be
    used if you have multiple installers in the same directory that use the same
    ``install.ini`` file and you don't want to download the additional
    installers.

    .. code-block:: bash

        ntp:
          4.2.8:
            installer: 'salt://win/repo/ntp/ntp-4.2.8-win32-setup.exe'
            full_name: Meinberg NTP Windows Client
            locale: en_US
            reboot: False
            cache_file: 'salt://win/repo/ntp/install.ini'
            install_flags: '/USEFILE=C:\salt\var\cache\salt\minion\files\base\win\repo\ntp\install.ini'
            uninstaller: 'NTP/uninst.exe'

    The following example demonstrates the use of ``cache_dir``. It assumes a
    file named ``install.ini`` resides in the same directory as the installer.

    .. code-block:: bash

        ntp:
          4.2.8:
            installer: 'salt://win/repo/ntp/ntp-4.2.8-win32-setup.exe'
            full_name: Meinberg NTP Windows Client
            locale: en_US
            reboot: False
            cache_dir: True
            install_flags: '/USEFILE=C:\salt\var\cache\salt\minion\files\base\win\repo\ntp\install.ini'
            uninstaller: 'NTP/uninst.exe'
    '''
    ret = {}
    saltenv = kwargs.pop('saltenv', 'base')
    refresh = salt.utils.is_true(refresh)
    # no need to call _refresh_db_conditional as list_pkgs will do it

    # Make sure name or pkgs is passed
    if not name and not pkgs:
        return 'Must pass a single package or a list of packages'

    # Ignore pkg_type from parse_targets, Windows does not support the
    # "sources" argument
    pkg_params = __salt__['pkg_resource.parse_targets'](name, pkgs, **kwargs)[0]

    if len(pkg_params) > 1:
        if kwargs.get('extra_install_flags') is not None:
            log.warning('\'extra_install_flags\' argument will be ignored for '
                        'multiple package targets')

    # Windows expects an Options dictionary containing 'version'
    for pkg in pkg_params:
        pkg_params[pkg] = {'version': pkg_params[pkg]}

    if pkg_params is None or len(pkg_params) == 0:
        log.error('No package definition found')
        return {}

    if not pkgs and len(pkg_params) == 1:
        # Only use the 'version' param if a single item was passed to the 'name'
        # parameter
        pkg_params = {
            name: {
                'version': kwargs.get('version'),
                'extra_install_flags': kwargs.get('extra_install_flags')
            }
        }

    # Get a list of currently installed software for comparison at the end
    old = list_pkgs(saltenv=saltenv, refresh=refresh)

    # Loop through each package
    changed = []
    latest = []
    for pkg_name, options in six.iteritems(pkg_params):

        # Load package information for the package
        pkginfo = _get_package_info(pkg_name, saltenv=saltenv)

        # Make sure pkginfo was found
        if not pkginfo:
            log.error('Unable to locate package {0}'.format(pkg_name))
            ret[pkg_name] = 'Unable to locate package {0}'.format(pkg_name)
            continue

        # Get the version number passed or the latest available (must be a string)
        version_num = ''
        if options:
            version_num = options.get('version', '')
            #  Using the salt cmdline with version=5.3 might be interpreted
            #  as a float it must be converted to a string in order for
            #  string matching to work.
            if not isinstance(version_num, six.string_types) and version_num is not None:
                version_num = str(version_num)

        if not version_num:
            version_num = _get_latest_pkg_version(pkginfo)

        # Check if the version is already installed
        if version_num in old.get(pkg_name, '').split(',') \
                or (pkg_name in old and old[pkg_name] == 'Not Found'):
            # Desired version number already installed
            ret[pkg_name] = {'current': version_num}
            continue

        # If version number not installed, is the version available?
        elif version_num not in pkginfo:
            log.error('Version {0} not found for package '
                      '{1}'.format(version_num, pkg_name))
            ret[pkg_name] = {'not found': version_num}
            continue

        if 'latest' in pkginfo:
            latest.append(pkg_name)

        # Get the installer settings from winrepo.p
        installer = pkginfo[version_num].get('installer', False)
        cache_dir = pkginfo[version_num].get('cache_dir', False)
        cache_file = pkginfo[version_num].get('cache_file', False)

        # Is there an installer configured?
        if not installer:
            log.error('No installer configured for version {0} of package '
                      '{1}'.format(version_num, pkg_name))
            ret[pkg_name] = {'no installer': version_num}
            continue

        # Is the installer in a location that requires caching
        if installer.startswith(('salt:', 'http:', 'https:', 'ftp:')):

            # Check for the 'cache_dir' parameter in the .sls file
            # If true, the entire directory will be cached instead of the
            # individual file. This is useful for installations that are not
            # single files
            if cache_dir and installer.startswith('salt:'):
                path, _ = os.path.split(installer)
                __salt__['cp.cache_dir'](path,
                                         saltenv,
                                         False,
                                         None,
                                         'E@init.sls$')

            # Check to see if the cache_file is cached... if passed
            if cache_file and cache_file.startswith('salt:'):

                # Check to see if the file is cached
                cached_file = __salt__['cp.is_cached'](cache_file, saltenv)
                if not cached_file:
                    cached_file = __salt__['cp.cache_file'](cache_file, saltenv)

                # Make sure the cached file is the same as the source
                if __salt__['cp.hash_file'](cache_file, saltenv) != \
                        __salt__['cp.hash_file'](cached_file):
                    cached_file = __salt__['cp.cache_file'](cache_file, saltenv)

                    # Check if the cache_file was cached successfully
                    if not cached_file:
                        log.error('Unable to cache {0}'.format(cache_file))
                        ret[pkg_name] = {
                            'failed to cache cache_file': cache_file
                        }
                        continue

            # Check to see if the installer is cached
            cached_pkg = __salt__['cp.is_cached'](installer, saltenv)
            if not cached_pkg:
                # It's not cached. Cache it, mate.
                cached_pkg = __salt__['cp.cache_file'](installer, saltenv)

                # Check if the installer was cached successfully
                if not cached_pkg:
                    log.error('Unable to cache file {0} '
                              'from saltenv: {1}'.format(installer, saltenv))
                    ret[pkg_name] = {'unable to cache': installer}
                    continue

            # Compare the hash of the cached installer to the source only if the
            # file is hosted on salt:
            if installer.startswith('salt:'):
                if __salt__['cp.hash_file'](installer, saltenv) != \
                        __salt__['cp.hash_file'](cached_pkg):
                    try:
                        cached_pkg = __salt__['cp.cache_file'](installer,
                                                               saltenv)
                    except MinionError as exc:
                        return '{0}: {1}'.format(exc, installer)

                    # Check if the installer was cached successfully
                    if not cached_pkg:
                        log.error('Unable to cache {0}'.format(installer))
                        ret[pkg_name] = {'unable to cache': installer}
                        continue
        else:
            # Run the installer directly (not hosted on salt:, https:, etc.)
            cached_pkg = installer

        # Fix non-windows slashes
        cached_pkg = cached_pkg.replace('/', '\\')
        cache_path, _ = os.path.split(cached_pkg)

        # Compare the hash sums
        source_hash = pkginfo[version_num].get('source_hash', False)
        if source_hash:
            source_sum = _get_source_sum(source_hash, cached_pkg, saltenv)
            log.debug('Source {0} hash: {1}'.format(source_sum['hash_type'],
                                                    source_sum['hsum']))

            cached_pkg_sum = salt.utils.get_hash(cached_pkg,
                                                 source_sum['hash_type'])
            log.debug('Package {0} hash: {1}'.format(source_sum['hash_type'],
                                                     cached_pkg_sum))

            if source_sum['hsum'] != cached_pkg_sum:
                raise SaltInvocationError(
                    ("Source hash '{0}' does not match package hash"
                     " '{1}'").format(source_sum['hsum'], cached_pkg_sum)
                )
            log.debug('Source hash matches package hash.')

        # Get install flags
        install_flags = '{0}'.format(pkginfo[version_num].get('install_flags'))
        if options and options.get('extra_install_flags'):
            install_flags = '{0} {1}'.format(
                install_flags,
                options.get('extra_install_flags', '')
            )

        #Compute msiexec string
        use_msiexec, msiexec = _get_msiexec(pkginfo[version_num].get('msiexec', False))

        # Install the software
        # Check Use Scheduler Option
        if pkginfo[version_num].get('use_scheduler', False):

            # Build Scheduled Task Parameters
            if use_msiexec:
                cmd = msiexec
                arguments = ['/i', cached_pkg]
                if pkginfo['version_num'].get('allusers', True):
                    arguments.append('ALLUSERS="1"')
                arguments.extend(salt.utils.shlex_split(install_flags))
            else:
                cmd = cached_pkg
                arguments = salt.utils.shlex_split(install_flags)

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
                log.error('Failed to install {0}'.format(pkg_name))
                log.error('Scheduled Task failed to run')
                ret[pkg_name] = {'install status': 'failed'}
        else:
            # Build the install command
            cmd = []
            if use_msiexec:
                cmd.extend([msiexec, '/i', cached_pkg])
                if pkginfo[version_num].get('allusers', True):
                    cmd.append('ALLUSERS="1"')
            else:
                cmd.append(cached_pkg)
            cmd.extend(salt.utils.shlex_split(install_flags))
            # Launch the command
            result = __salt__['cmd.run_all'](cmd,
                                             cache_path,
                                             output_loglevel='quiet',
                                             python_shell=False,
                                             redirect_stderr=True)
            if not result['retcode']:
                ret[pkg_name] = {'install status': 'success'}
                changed.append(pkg_name)
            elif result['retcode'] == 3010:
                # 3010 is ERROR_SUCCESS_REBOOT_REQUIRED
                report_reboot_exit_codes = kwargs.pop(
                    'report_reboot_exit_codes',
                    True
                    )
                if report_reboot_exit_codes:
                    __salt__['system.set_reboot_required_witnessed']()
                ret[pkg_name] = {'install status': 'success, reboot required'}
                changed.append(pkg_name)
            else:
                log.error('Failed to install {0}'.format(pkg_name))
                log.error('retcode {0}'.format(result['retcode']))
                log.error('installer output: {0}'.format(result['stdout']))
                ret[pkg_name] = {'install status': 'failed'}

    # Get a new list of installed software
    new = list_pkgs(saltenv=saltenv)

    # For installers that have no specific version (ie: chrome)
    # The software definition file will have a version of 'latest'
    # In that case there's no way to know which version has been installed
    # Just return the current installed version
    if latest:
        for pkg_name in latest:
            if old.get(pkg_name, 'old') == new.get(pkg_name, 'new'):
                ret[pkg_name] = {'current': new[pkg_name]}

    # Check for changes in the registry
    difference = salt.utils.compare_dicts(old, new)

    # Compare the software list before and after
    # Add the difference to ret
    ret.update(difference)

    return ret