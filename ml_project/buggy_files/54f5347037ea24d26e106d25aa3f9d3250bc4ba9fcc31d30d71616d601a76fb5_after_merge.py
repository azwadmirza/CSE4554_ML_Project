def info(*packages):
    '''
    Returns a detailed summary of package information for provided package names.
    If no packages are specified, all packages will be returned.

    .. versionadded:: 2015.8.1

    packages
        The names of the packages for which to return information.

    CLI example:

    .. code-block:: bash

        salt '*' lowpkg.info
        salt '*' lowpkg.info apache2 bash
    '''
    # Get the missing information from the /var/lib/dpkg/available, if it is there.
    # However, this file is operated by dselect which has to be installed.
    dselect_pkg_avail = _get_pkg_ds_avail()

    ret = dict()
    for pkg in _get_pkg_info(*packages):
        # Merge extra information from the dselect, if available
        for pkg_ext_k, pkg_ext_v in dselect_pkg_avail.get(pkg['package'], {}).items():
            if pkg_ext_k not in pkg:
                pkg[pkg_ext_k] = pkg_ext_v
        # Remove "technical" keys
        for t_key in ['installed_size', 'depends', 'recommends',
                      'provides', 'replaces', 'conflicts', 'bugs',
                      'description-md5', 'task']:
            if t_key in pkg:
                del pkg[t_key]

        lic = _get_pkg_license(pkg['package'])
        if lic:
            pkg['license'] = lic
        ret[pkg['package']] = pkg

    return ret