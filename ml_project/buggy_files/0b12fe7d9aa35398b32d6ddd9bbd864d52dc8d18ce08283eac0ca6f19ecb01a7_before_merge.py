def version(*names, **kwargs):
    '''
    Returns a version if the package is installed, else returns an empty string

    CLI Example::

        salt '*' pkg.version <package name>
    '''
    win_names = []
    ret = {}
    if len(names) == 1:
        versions = _get_package_info(names[0])
        if versions:
            for val in versions.itervalues():
                if 'full_name' in val and len(val.get('full_name', '')) > 0:
                    win_names.append(val.get('full_name', ''))
        else:
            win_names.append(names[0])
        val = __salt__['pkg_resource.version'](win_names[0], **kwargs)
        if len(val):
            return val
        return ''
    if len(names) > 1:
        reverse_dict = {}
        for name in names:
            ret[name] = ''
            versions = _get_package_info(name)
            if versions:
                for val in versions.itervalues():
                    if 'full_name' in val and len(val.get('full_name', '')) > 0:
                        reverse_dict[val.get('full_name', '')] = name
                        win_names.append(val.get('full_name', ''))
            else:
                win_names.append(name)
        nums = __salt__['pkg_resource.version'](*win_names, **kwargs)
        if len(nums):
            for num, val in nums.iteritems():
                if len(val) > 0:
                    try:
                        ret[reverse_dict[num]] = val
                    except KeyError:
                        ret[num] = val
            return ret
        return dict([(x, '') for x in names])
    return ret