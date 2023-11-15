def _check_if_installed(prefix, state_pkg_name, version_spec, ignore_installed,
                        force_reinstall, upgrade, user, cwd, bin_env, env_vars,
                        pip_list=False, **kwargs):
    '''
    Takes a package name and version specification (if any) and checks it is
    installed

    Keyword arguments include:
        pip_list: optional dict of installed pip packages, and their versions,
            to search through to check if the package is installed. If not
            provided, one will be generated in this function by querying the
            system.

    Returns:
     result: None means the command failed to run
     result: True means the package is installed
     result: False means the package is not installed
    '''
    ret = {'result': False, 'comment': None}

    # If we are not passed a pip list, get one:
    pip_list = salt.utils.data.CaseInsensitiveDict(
        pip_list or __salt__['pip.list'](prefix, bin_env=bin_env,
                                         user=user, cwd=cwd,
                                         env_vars=env_vars, **kwargs)
    )

    # If the package was already installed, check
    # the ignore_installed and force_reinstall flags
    if ignore_installed is False and prefix in pip_list:
        if force_reinstall is False and not upgrade:
            # Check desired version (if any) against currently-installed
            if (
                any(version_spec) and
                _fulfills_version_spec(pip_list[prefix], version_spec)
            ) or (not any(version_spec)):
                ret['result'] = True
                ret['comment'] = ('Python package {0} was already '
                                  'installed'.format(state_pkg_name))
                return ret
        if force_reinstall is False and upgrade:
            # Check desired version (if any) against currently-installed
            include_alpha = False
            include_beta = False
            include_rc = False
            if any(version_spec):
                for spec in version_spec:
                    if 'a' in spec[1]:
                        include_alpha = True
                    if 'b' in spec[1]:
                        include_beta = True
                    if 'rc' in spec[1]:
                        include_rc = True
            available_versions = __salt__['pip.list_all_versions'](
                prefix, bin_env=bin_env, include_alpha=include_alpha,
                include_beta=include_beta, include_rc=include_rc, user=user,
                cwd=cwd)
            desired_version = ''
            if any(version_spec):
                for version in reversed(available_versions):
                    if _fulfills_version_spec(version, version_spec):
                        desired_version = version
                        break
            else:
                desired_version = available_versions[-1]
            if not desired_version:
                ret['result'] = True
                ret['comment'] = ('Python package {0} was already '
                                  'installed and\nthe available upgrade '
                                  'doesn\'t fulfills the version '
                                  'requirements'.format(prefix))
                return ret
            if _pep440_version_cmp(pip_list[prefix], desired_version) == 0:
                ret['result'] = True
                ret['comment'] = ('Python package {0} was already '
                                  'installed'.format(state_pkg_name))
                return ret

    return ret