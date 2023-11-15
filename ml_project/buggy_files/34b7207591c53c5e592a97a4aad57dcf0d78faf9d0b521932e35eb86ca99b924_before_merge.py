def installed(name, version=None, source=None, force=False, pre_versions=False,
              install_args=None, override_args=False, force_x86=False,
              package_args=None, allow_multiple=False):
    '''
    Installs a package if not already installed

    Args:

        name (str):
            The name of the package to be installed. Required.

        version (str):
            Install a specific version of the package. Defaults to latest
            version. If the version is different to the one installed then the
            specified version will be installed. Default is None.

        source (str):
            Chocolatey repository (directory, share or remote URL, feed).
            Defaults to the official Chocolatey feed. Default is None.

        force (bool):
            Reinstall the current version of an existing package. Do not use
            with ``allow_multiple``. Default is False.

        pre_versions (bool):
            Include pre-release packages. Default is False.

        install_args (str):
            Install arguments you want to pass to the installation process, i.e
            product key or feature list. Default is None.

        override_args (bool):
            Set to True if you want to override the original install arguments
            (for the native installer) in the package and use your own. When
            this is set to False install_args will be appended to the end of the
            default arguments. Default is False.

        force_x86 (bool):
            Force x86 (32bit) installation on 64 bit systems. Default is False.

        package_args (str):
            Arguments you want to pass to the package. Default is None.

        allow_multiple (bool):
            Allow mulitiple versions of the package to be installed. Do not use
            with ``force``. Does not work with all packages. Default is False.

            .. versionadded:: 2017.7.0

    .. code-block:: yaml

        Installsomepackage:
          chocolatey.installed:
            - name: packagename
            - version: '12.04'
            - source: 'mychocolatey/source'
            - force: True
    '''
    if force and allow_multiple:
        raise SaltInvocationError(
            'Cannot use \'force\' in conjunction with \'allow_multiple\'')

    ret = {'name': name,
           'result': True,
           'changes': {},
           'comment': ''}

    # Get list of currently installed packages
    pre_install = __salt__['chocolatey.list'](local_only=True)

    # Determine action
    # Package not installed
    if name not in [package.split('|')[0].lower() for package in pre_install.splitlines()]:
        if version:
            ret['changes'] = {name: 'Version {0} will be installed'
                                    ''.format(version)}
        else:
            ret['changes'] = {name: 'Will be installed'}
    # Package installed
    else:
        version_info = __salt__['chocolatey.version'](name, check_remote=True)

        full_name = name
        lower_name = name.lower()
        for pkg in version_info:
            if lower_name == pkg.lower():
                full_name = pkg

        available_version = version_info[full_name]['available'][0]
        version = version if version else available_version

        if force:
            ret['changes'] = {name: 'Version {0} will be forcibly installed'
                                    ''.format(version)}
        elif allow_multiple:
            ret['changes'] = {name: 'Version {0} will be installed side by side'
                                    ''.format(version)}
        else:
            ret['comment'] = 'The Package {0} is already installed'.format(name)
            return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'The installation was tested'
        return ret

    # Install the package
    result = __salt__['chocolatey.install'](name=name,
                                            version=version,
                                            source=source,
                                            force=force,
                                            pre_versions=pre_versions,
                                            install_args=install_args,
                                            override_args=override_args,
                                            force_x86=force_x86,
                                            package_args=package_args,
                                            allow_multiple=allow_multiple)

    if 'Running chocolatey failed' not in result:
        ret['result'] = True
    else:
        ret['result'] = False

    if not ret['result']:
        ret['comment'] = 'Failed to install the package {0}'.format(name)

    # Get list of installed packages after 'chocolatey.install'
    post_install = __salt__['chocolatey.list'](local_only=True)

    ret['changes'] = salt.utils.compare_dicts(pre_install, post_install)

    return ret