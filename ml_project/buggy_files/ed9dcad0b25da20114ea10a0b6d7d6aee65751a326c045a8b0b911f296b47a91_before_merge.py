def _changes(name, admin):
    '''
    Get necessary changes to given user account
    '''

    existing_user = __salt__['influxdb.user_info'](name)
    changes = {}

    if existing_user['admin'] != admin:
        changes['admin'] = admin

    return changes