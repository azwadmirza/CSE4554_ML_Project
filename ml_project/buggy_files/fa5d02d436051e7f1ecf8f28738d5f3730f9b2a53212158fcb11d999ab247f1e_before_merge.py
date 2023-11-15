def uninstalled(name, version=None, uninstall_args=None, override_args=False):
    '''
    Uninstalls a package

    name
      The name of the package to be uninstalled

    version
      Uninstalls a specific version of the package. Defaults to latest
      version installed.

    uninstall_args
      A list of uninstall arguments you want to pass to the uninstallation
      process i.e product key or feature list

    override_args
      Set to true if you want to override the original uninstall arguments (
      for the native uninstaller)in the package and use your own.
      When this is set to False uninstall_args will be appended to the end of
      the default arguments

    .. code-block: yaml

      Removemypackage:
        chocolatey.uninstalled:
          - name: mypackage
          - version: '21.5'

    '''

    ret = {'name': name,
           'result': True,
           'changes': {},
           'comment': ''}

    # Get list of currently installed packages
    pre_uninstall = __salt__['chocolatey.list'](local_only=True)

    # Determine if package is installed
    if name in [package.split('|')[0].lower() for package in pre_uninstall.splitlines()]:
        ret['changes'] = {name: '{0} version {1} will be removed'
                                ''.format(name, pre_uninstall[name][0])}
    else:
        ret['comment'] = 'The package {0} is not installed'.format(name)
        return ret

    if __opts__['test']:
        ret['result'] = None
        ret['comment'] = 'The uninstall was tested'
        return ret

    # Uninstall the package
    result = __salt__['chocolatey.uninstall'](name,
                                              version,
                                              uninstall_args,
                                              override_args)

    if 'Running chocolatey failed' not in result:
        ret['result'] = True
    else:
        ret['result'] = False

    if not ret['result']:
        ret['comment'] = 'Failed to uninstall the package {0}'.format(name)

    # Get list of installed packages after 'chocolatey.uninstall'
    post_uninstall = __salt__['chocolatey.list'](local_only=True)

    ret['changes'] = salt.utils.compare_dicts(pre_uninstall, post_uninstall)

    return ret