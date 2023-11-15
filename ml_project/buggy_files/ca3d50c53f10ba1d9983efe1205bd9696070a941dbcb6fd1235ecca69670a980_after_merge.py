def _check_if_installed(prefix, state_pkg_name, version_spec,
                        ignore_installed, force_reinstall,
                        upgrade, user, cwd, bin_env):

    # result: None means the command failed to run
    # result: True means the package is installed
    # result: False means the package is not installed
    ret = {'result': False, 'comment': None}

    # Check if the requested packated is already installed.
    try:
        pip_list = __salt__['pip.list'](prefix, bin_env=bin_env,
                                        user=user, cwd=cwd)
        prefix_realname = _find_key(prefix, pip_list)
    except (CommandNotFoundError, CommandExecutionError) as err:
        ret['result'] = False
        ret['comment'] = 'Error installing {0!r}: {1}'.format(state_pkg_name,
                                                              err)
        return ret

    # If the package was already installed, check
    # the ignore_installed and force_reinstall flags
    if ignore_installed is False and prefix_realname is not None:
        if force_reinstall is False and not upgrade:
            # Check desired version (if any) against currently-installed
            if (
                any(version_spec) and
                _fulfills_version_spec(pip_list[prefix_realname],
                                       version_spec)
            ) or (not any(version_spec)):
                ret['result'] = True
                ret['comment'] = ('Python package {0} was already '
                                  'installed'.format(state_pkg_name))
                return ret

    return ret