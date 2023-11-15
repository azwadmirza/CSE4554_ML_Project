def info_installed(*names):
    '''
    Return the information of the named package(s) installed on the system.

    .. versionadded:: 2015.8.1

    names
        The names of the packages for which to return information.

    CLI example:

    .. code-block:: bash

        salt '*' pkg.info_installed <package1>
        salt '*' pkg.info_installed <package1> <package2> <package3> ...
    '''
    ret = dict()
    for pkg_name, pkg_nfo in __salt__['lowpkg.info'](*names).items():
        t_nfo = dict()
        # Translate dpkg-specific keys to a common structure
        for key, value in pkg_nfo.items():
            if key == 'package':
                t_nfo['name'] = value
            elif key == 'origin':
                t_nfo['vendor'] = value
            elif key == 'section':
                t_nfo['group'] = value
            elif key == 'maintainer':
                t_nfo['packager'] = value
            elif key == 'homepage':
                t_nfo['url'] = value
            else:
                t_nfo[key] = value

        ret[pkg_name] = t_nfo

    return ret