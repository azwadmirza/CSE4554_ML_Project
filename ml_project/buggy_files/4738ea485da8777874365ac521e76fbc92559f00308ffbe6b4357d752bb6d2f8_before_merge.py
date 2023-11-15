def info(name):
    '''
    Return user information

    CLI Example:

    .. code-block:: bash

        salt '*' user.info root
    '''
    ret = {}
    items = {}
    for line in __salt__['cmd.run']('net user {0}'.format(name)).splitlines():
        if 'name could not be found' in line:
            return {}
        if 'successfully' not in line:
            comps = line.split('    ', 1)
            if not len(comps) > 1:
                continue
            items[comps[0].strip()] = comps[1].strip()
    grouplist = []
    groups = items['Local Group Memberships'].split('  ')
    for group in groups:
        if not group:
            continue
        grouplist.append(group.strip(' *'))

    ret['fullname'] = items['Full Name']
    ret['name'] = items['User name']
    ret['comment'] = items['Comment']
    ret['active'] = items['Account active']
    ret['logonscript'] = items['Logon script']
    ret['profile'] = items['User profile']
    if not ret['profile']:
        ret['profile'] = _get_userprofile_from_registry(name)
    ret['home'] = items['Home directory']
    ret['groups'] = grouplist
    ret['gid'] = ''

    return ret