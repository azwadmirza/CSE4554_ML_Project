def _changes(name, admin, **client_args):
    '''
    Get necessary changes to given user account
    '''

    existing_user = __salt__['influxdb.user_info'](name, **client_args)
    changes = {}

    if existing_user['admin'] != admin:
        changes['admin'] = admin

    return changes