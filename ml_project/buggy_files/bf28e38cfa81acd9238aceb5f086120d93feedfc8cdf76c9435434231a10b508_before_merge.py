def installed(name,
              dir=None,
              runas=None,
              user=None,
              force_reinstall=False,
              **kwargs):
    '''
    Verify that the given package is installed and is at the correct version
    (if specified).

    dir
        The target directory in which to install the package, or None for
        global installation

    runas
        The user to run NPM with

        .. deprecated:: 0.17.0

    user
        The user to run NPM with

        .. versionadded:: 0.17.0

    force_reinstall
        Install the package even if it is already installed
    '''
    ret = {'name': name, 'result': None, 'comment': '', 'changes': {}}

    salt.utils.warn_until(
        (0, 18),
        'Please remove \'runas\' support at this stage. \'user\' support was '
        'added in 0.17.0',
        _dont_call_warnings=True
    )
    if runas:
        # Warn users about the deprecation
        ret.setdefault('warnings', []).append(
            'The \'runas\' argument is being deprecated in favor or \'user\', '
            'please update your state files.'
        )
    if user is not None and runas is not None:
        # user wins over runas but let warn about the deprecation.
        ret.setdefault('warnings', []).append(
            'Passed both the \'runas\' and \'user\' arguments. Please don\'t. '
            '\'runas\' is being ignored in favor of \'user\'.'
        )
        runas = None
    elif runas is not None:
        # Support old runas usage
        user = runas
        runas = None

    prefix = name.split('@')[0].strip()

    try:
        installed_pkgs = __salt__['npm.list'](pkg=name, dir=dir)
    except (CommandNotFoundError, CommandExecutionError) as err:
        ret['result'] = False
        ret['comment'] = 'Error installing \'{0}\': {1}'.format(name, err)
        return ret

    installed_pkgs = dict((p.lower(), info) for p, info in installed_pkgs.items())

    if prefix.lower() in installed_pkgs:
        if force_reinstall is False:
            ret['result'] = True
            ret['comment'] = 'Package {0} satisfied by {1}@{2}'.format(
                    name, prefix, installed_pkgs[prefix.lower()]['version'])
            return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'NPM package {0} is set to be installed'.format(name)
        return ret

    try:
        call = __salt__['npm.install'](
            pkg=name,
            dir=dir,
            runas=user
        )
    except (CommandNotFoundError, CommandExecutionError) as err:
        ret['result'] = False
        ret['comment'] = 'Error installing \'{0}\': {1}'.format(name, err)
        return ret

    if call or isinstance(call, list) or isinstance(call, dict):
        ret['result'] = True
        version = call[0]['version']
        pkg_name = call[0]['name']
        ret['changes']['{0}@{1}'.format(pkg_name, version)] = 'Installed'
        ret['comment'] = 'Package {0} was successfully installed'.format(name)
    else:
        ret['result'] = False
        ret['comment'] = 'Could not install package'

    return ret