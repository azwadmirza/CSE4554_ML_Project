def list_upgrades(refresh=True, saltenv='base'):
    '''
    List all available package upgrades on this system

    CLI Example:

    .. code-block:: bash

        salt '*' pkg.list_upgrades
    '''
    if salt.utils.is_true(refresh):
        refresh_db(saltenv)

    ret = {}
    for name, data in six.iteritems(get_repo_data(saltenv).get('repo', {})):
        if version(name):
            latest = latest_version(name)
            if latest:
                ret[name] = latest
    return ret