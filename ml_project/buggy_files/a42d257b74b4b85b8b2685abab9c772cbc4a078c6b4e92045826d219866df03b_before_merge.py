def installed(name,
              pkgs=None,
              dir=None,
              user=None,
              force_reinstall=False,
              registry=None,
              env=None):
    '''
    Verify that the given package is installed and is at the correct version
    (if specified).

    .. code-block:: yaml

        coffee-script:
          npm.installed:
            - user: someuser

        coffee-script@1.0.1:
          npm.installed: []

    name
        The package to install

        .. versionchanged:: 2014.7.2
            This parameter is no longer lowercased by salt so that
            case-sensitive NPM package names will work.

    pkgs
        A list of packages to install with a single npm invocation; specifying
        this argument will ignore the ``name`` argument

        .. versionadded:: 2014.7.0

    dir
        The target directory in which to install the package, or None for
        global installation

    user
        The user to run NPM with

        .. versionadded:: 0.17.0

    registry
        The NPM registry from which to install the package

        .. versionadded:: 2014.7.0

    env
        A list of environment variables to be set prior to execution. The
        format is the same as the :py:func:`cmd.run <salt.states.cmd.run>`.
        state function.

        .. versionadded:: 2014.7.0

    force_reinstall
        Install the package even if it is already installed
    '''
    ret = {'name': name, 'result': None, 'comment': '', 'changes': {}}

    if pkgs is not None:
        pkg_list = pkgs
    else:
        pkg_list = [name]

    try:
        installed_pkgs = __salt__['npm.list'](dir=dir, runas=user, env=env)
    except (CommandNotFoundError, CommandExecutionError) as err:
        ret['result'] = False
        ret['comment'] = 'Error looking up {0!r}: {1}'.format(name, err)
        return ret
    else:
        installed_pkgs = dict((p, info)
                for p, info in six.iteritems(installed_pkgs))

    pkgs_satisfied = []
    pkgs_to_install = []

    def _pkg_is_installed(pkg, installed_pkgs):
        '''
        Helper function to determine if a package is installed

        This performs more complex comparison than just checking
        keys, such as examining source repos to see if the package
        was installed by a different name from the same repo

        :pkg str: The package to compare
        :installed_pkgs: A dictionary produced by npm list --json
        '''
        if pkg_name in installed_pkgs:
            return True
        # Check to see if we are trying to install from a URI
        elif '://' in pkg_name:  # TODO Better way?
            for pkg_details in installed_pkgs.values():
                pkg_from = pkg_details.get('from', '').split('://')[1]
                if pkg_name.split('://')[1] == pkg_from:
                    return True
        return False

    for pkg in pkg_list:
        pkg_name, _, pkg_ver = pkg.partition('@')
        pkg_name = pkg_name.strip()

        if force_reinstall is True:
            pkgs_to_install.append(pkg)
            continue
        if not _pkg_is_installed(pkg, installed_pkgs):
            pkgs_to_install.append(pkg)
            continue

        if pkg_name in installed_pkgs:
            installed_name_ver = '{0}@{1}'.format(pkg_name,
                    installed_pkgs[pkg_name]['version'])

            # If given an explicit version check the installed version matches.
            if pkg_ver:
                if installed_pkgs[pkg_name].get('version') != pkg_ver:
                    pkgs_to_install.append(pkg)
                else:
                    pkgs_satisfied.append(installed_name_ver)

                continue
            else:
                pkgs_satisfied.append(installed_name_ver)
                continue

    if __opts__['test']:
        ret['result'] = None

        comment_msg = []
        if pkgs_to_install:
            comment_msg.append('NPM package(s) {0!r} are set to be installed'
                .format(', '.join(pkgs_to_install)))

            ret['changes'] = {'old': [], 'new': pkgs_to_install}

        if pkgs_satisfied:
            comment_msg.append('Package(s) {0!r} satisfied by {1}'
                .format(', '.join(pkg_list), ', '.join(pkgs_satisfied)))

        ret['comment'] = '. '.join(comment_msg)
        return ret

    if not pkgs_to_install:
        ret['result'] = True
        ret['comment'] = ('Package(s) {0!r} satisfied by {1}'
                .format(', '.join(pkg_list), ', '.join(pkgs_satisfied)))
        return ret

    try:
        cmd_args = {
            'dir': dir,
            'runas': user,
            'registry': registry,
            'env': env,
        }

        if pkgs is not None:
            cmd_args['pkgs'] = pkgs
        else:
            cmd_args['pkg'] = pkg_name

        call = __salt__['npm.install'](**cmd_args)
    except (CommandNotFoundError, CommandExecutionError) as err:
        ret['result'] = False
        ret['comment'] = 'Error installing {0!r}: {1}'.format(
                ', '.join(pkg_list), err)
        return ret

    if call and (isinstance(call, list) or isinstance(call, dict)):
        ret['result'] = True
        ret['changes'] = {'old': [], 'new': pkgs_to_install}
        ret['comment'] = 'Package(s) {0!r} successfully installed'.format(
                ', '.join(pkgs_to_install))
    else:
        ret['result'] = False
        ret['comment'] = 'Could not install package(s) {0!r}'.format(
                ', '.join(pkg_list))

    return ret