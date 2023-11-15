def grant_exists(grant,
                 database,
                 user,
                 host='localhost',
                 grant_option=False,
                 escape=True,
                 **connection_args):
    '''
    Checks to see if a grant exists in the database

    CLI Example:

    .. code-block:: bash

        salt '*' mysql.grant_exists \
             'SELECT,INSERT,UPDATE,...' 'database.*' 'frank' 'localhost'
    '''

    server_version = version(**connection_args)
    if 'ALL' in grant:
        if salt.utils.versions.version_cmp(server_version, '8.0') >= 0:
            grant = ','.join([i for i in __all_privileges__])
        else:
            grant = 'ALL PRIVILEGES'

    try:
        target = __grant_generate(
            grant, database, user, host, grant_option, escape
        )
    except Exception:
        log.error('Error during grant generation.')
        return False

    grants = user_grants(user, host, **connection_args)

    if grants is False:
        log.error('Grant does not exist or may not be ordered properly. In some cases, '
                  'this could also indicate a connection error. Check your configuration.')
        return False

    # Combine grants that match the same database
    _grants = {}
    for grant in grants:
        grant_token = _grant_to_tokens(grant)
        if grant_token['database'] not in _grants:
            _grants[grant_token['database']] = {'user': grant_token['user'],
                                                'database': grant_token['database'],
                                                'host': grant_token['host'],
                                                'grant': grant_token['grant']}
        else:
            _grants[grant_token['database']]['grant'].extend(grant_token['grant'])

    target_tokens = _grant_to_tokens(target)
    for database, grant_tokens in _grants.items():
        try:
            _grant_tokens = {}
            _target_tokens = {}

            _grant_matches = [True if i in grant_tokens['grant']
                              else False for i in target_tokens['grant']]

            for item in ['user', 'database', 'host']:
                _grant_tokens[item] = grant_tokens[item].replace('"', '').replace('\\', '').replace('`', '')
                _target_tokens[item] = target_tokens[item].replace('"', '').replace('\\', '').replace('`', '')

            if _grant_tokens['user'] == _target_tokens['user'] and \
                    _grant_tokens['database'] == _target_tokens['database'] and \
                    _grant_tokens['host'] == _target_tokens['host'] and \
                    all(_grant_matches):
                return True
            else:
                log.debug('grants mismatch \'%s\'<>\'%s\'', grant_tokens, target_tokens)

        except Exception as exc:  # Fallback to strict parsing
            log.exception(exc)
            if grants is not False and target in grants:
                log.debug('Grant exists.')
                return True

    log.debug('Grant does not exist, or is perhaps not ordered properly?')
    return False