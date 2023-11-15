def _update_gecos(name, key, value, root=None):
    '''
    Common code to change a user's GECOS information
    '''
    if value is None:
        value = ''
    elif not isinstance(value, six.string_types):
        value = str(value)
    pre_info = _get_gecos(name)
    if not pre_info:
        return False
    if value == pre_info[key]:
        return True
    gecos_data = copy.deepcopy(pre_info)
    gecos_data[key] = value

    cmd = ['usermod', '-c', _build_gecos(gecos_data), name]

    if root is not None and __grains__['kernel'] != 'AIX':
        cmd.extend(('-R', root))

    __salt__['cmd.run'](cmd, python_shell=False)
    post_info = info(name)
    return _get_gecos(name).get(key) == value