def info(name):
    '''
    Return user information

    CLI Example:

    .. code-block:: bash

        salt '*' user.info root
    '''
    ret = {}
    items = {}
    try:
        items = win32net.NetUserGetInfo(None, name, 4)
    except win32net.error:
        pass

    if items:
        groups = []
        try:
            groups = win32net.NetUserGetLocalGroups(None, name)
        except win32net.error:
            pass

        ret['fullname'] = items['full_name']
        ret['name'] = items['name']
        ret['comment'] = items['comment']
        ret['active'] = (not bool(items['flags'] & win32netcon.UF_ACCOUNTDISABLE))
        ret['logonscript'] = items['script_path']
        ret['profile'] = items['profile']
        if not ret['profile']:
            ret['profile'] = _get_userprofile_from_registry(name)
        ret['home'] = items['home_dir']
        ret['groups'] = groups
        ret['gid'] = ''

    return ret