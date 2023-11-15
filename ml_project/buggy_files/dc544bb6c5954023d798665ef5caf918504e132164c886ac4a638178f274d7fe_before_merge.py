def user_grants(user,
                host='localhost', **connection_args):
    '''
    Shows the grants for the given MySQL user (if it exists)

    CLI Example:

    .. code-block:: bash

        salt '*' mysql.user_grants 'frank' 'localhost'
    '''
    if not user_exists(user, host, **connection_args):
        log.info('User \'%s\'@\'%s\' does not exist', user, host)
        return False

    dbc = _connect(**connection_args)
    if dbc is None:
        return False
    cur = dbc.cursor()
    qry = 'SHOW GRANTS FOR %(user)s@%(host)s'
    args = {}
    args['user'] = user
    args['host'] = host
    try:
        _execute(cur, qry, args)
    except MySQLdb.OperationalError as exc:
        err = 'MySQL Error {0}: {1}'.format(*exc)
        __context__['mysql.error'] = err
        log.error(err)
        return False

    ret = []
    results = cur.fetchall()
    for grant in results:
        tmp = grant[0].split(' IDENTIFIED BY')[0]
        if 'WITH GRANT OPTION' in grant[0] and 'WITH GRANT OPTION' not in tmp:
            tmp = '{0} WITH GRANT OPTION'.format(tmp)
        ret.append(tmp)
    log.debug(ret)
    return ret