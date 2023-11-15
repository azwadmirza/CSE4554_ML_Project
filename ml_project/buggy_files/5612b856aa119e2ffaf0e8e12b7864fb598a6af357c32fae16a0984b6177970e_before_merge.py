def install(name=None, refresh=False, pkgs=None, version=None, test=False, **kwargs):
    '''
    Install the named package using the IPS pkg command.
    Accepts full or partial FMRI.

    Returns a dict containing the new package names and versions::

        {'<package>': {'old': '<old-version>',
                       'new': '<new-version>'}}


    Multiple Package Installation Options:

    pkgs
        A list of packages to install. Must be passed as a python list.


    CLI Example:

    .. code-block:: bash

        salt '*' pkg.install vim
        salt '*' pkg.install pkg://solaris/editor/vim
        salt '*' pkg.install pkg://solaris/editor/vim refresh=True
        salt '*' pkg.install pkgs='["foo", "bar"]'
    '''
    if not pkgs:
        if is_installed(name):
            return 'Package already installed.'

    if refresh:
        refresh_db(full=True)

    pkg2inst = ''
    if pkgs:    # multiple packages specified
        for pkg in pkgs:
            if list(pkg.items())[0][1]:   # version specified
                pkg2inst += '{0}@{1} '.format(list(pkg.items())[0][0],
                                              list(pkg.items())[0][1])
            else:
                pkg2inst += '{0} '.format(list(pkg.items())[0][0])
        log.debug('Installing these packages instead of %s: %s',
                  name, pkg2inst)

    else:   # install single package
        if version:
            pkg2inst = "{0}@{1}".format(name, version)
        else:
            pkg2inst = "{0}".format(name)

    cmd = ['pkg', 'install', '-v', '--accept']
    if test:
        cmd.append('-n')

    # Get a list of the packages before install so we can diff after to see
    # what got installed.
    old = list_pkgs()

    # Install or upgrade the package
    # If package is already installed
    cmd.append(pkg2inst)

    out = __salt__['cmd.run_all'](cmd, output_loglevel='trace')

    # Get a list of the packages again, including newly installed ones.
    __context__.pop('pkg.list_pkgs', None)
    new = list_pkgs()
    ret = salt.utils.data.compare_dicts(old, new)

    if out['retcode'] != 0:
        raise CommandExecutionError(
            'Error occurred installing package(s)',
            info={
                'changes': ret,
                'retcode': ips_pkg_return_values[out['retcode']],
                'errors': [out['stderr']]
            }
        )

    # No error occurred
    if test:
        return 'Test succeeded.'

    return ret