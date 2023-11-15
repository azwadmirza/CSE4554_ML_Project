def user_list(user=None, password=None, host=None, port=None, database='admin'):
    '''
    List users of a Mongodb database

    CLI Example:

    .. code-block:: bash

        salt '*' mongodb.user_list <user> <password> <host> <port> <database>
    '''
    conn = _connect(user, password, host, port)
    if not conn:
        return 'Failed to connect to mongo database'

    try:
        log.info('Listing users')
        mdb = pymongo.database.Database(conn, database)

        output = []
        mongodb_version = mdb.eval('db.version()')

        if StrictVersion(mongodb_version) >= StrictVersion('2.6'):
            for user in mdb.eval('db.getUsers()'):
                output.append([
                    ('user', user['user']),
                    ('roles', user['roles'])
                ])
        else:
            for user in mdb.system.users.find():
                output.append([
                    ('user', user['user']),
                    ('readOnly', user.get('readOnly', 'None'))
                ])
        return output

    except pymongo.errors.PyMongoError as err:
        log.error(
            'Listing users failed with error: {0}'.format(
                str(err)
            )
        )
        return str(err)