def grant_revoke(grant,
                 database,
                 user,
                 host='localhost',
                 grant_option=False,
                 escape=True,
                 **connection_args):
    '''
    Removes a grant from the MySQL server.

    CLI Example:

    .. code-block:: bash

        salt '*' mysql.grant_revoke 'SELECT,INSERT,UPDATE' 'database.*' 'frank' 'localhost'
    '''
    # todo: validate grant
    dbc = _connect(**connection_args)
    if dbc is None:
        return False
    cur = dbc.cursor()

    if grant_option:
        grant += ', GRANT OPTION'
    qry = 'REVOKE {0} ON {1} FROM {2!r}@{3!r};'.format(
        grant, database, user, host
    )
    log.debug('Query: {0}'.format(qry))
    try:
        cur.execute(qry)
    except MySQLdb.OperationalError as exc:
        err = 'MySQL Error {0}: {1}'.format(*exc)
        __context__['mysql.error'] = err
        log.error(err)
        return False

    if not grant_exists(grant, database, user, host, grant_option, escape, **connection_args):
        log.info(
            'Grant {0!r} on {1!r} for user {2!r} has been '
            'revoked'.format(grant, database, user)
        )
        return True

    log.info(
        'Grant {0!r} on {1!r} for user {2!r} has NOT been '
        'revoked'.format(grant, database, user)
    )
    return False