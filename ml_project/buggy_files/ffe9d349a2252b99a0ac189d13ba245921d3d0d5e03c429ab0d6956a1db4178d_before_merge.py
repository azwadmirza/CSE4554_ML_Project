def list_pkgs(versions_as_list=False, **kwargs):
    '''
    List the packages currently installed in a dict::

        {'<package_name>': '<version>'}

    CLI Example:

    .. code-block:: bash

        salt '*' pkg.list_pkgs
        salt '*' pkg.list_pkgs versions_as_list=True
    '''
    versions_as_list = salt.utils.is_true(versions_as_list)
    # not yet implemented or not applicable
    if any([salt.utils.is_true(kwargs.get(x))
            for x in ('removed', 'purge_desired')]):
        return {}

    ret = {}
    name_map = _get_name_map()
    for pkg_name, val in six.iteritems(_get_reg_software()):
        if pkg_name in name_map:
            key = name_map[pkg_name]
            if val in ['(value not set)', 'Not Found', None, False]:
                # Look up version from winrepo
                pkg_info = _get_package_info(key)
                if not pkg_info:
                    continue
                for pkg_ver in pkg_info.keys():
                    if pkg_info[pkg_ver]['full_name'] == pkg_name:
                        val = pkg_ver
        else:
            key = pkg_name
        __salt__['pkg_resource.add_pkg'](ret, key, val)

    __salt__['pkg_resource.sort_pkglist'](ret)
    if not versions_as_list:
        __salt__['pkg_resource.stringify'](ret)
    return ret