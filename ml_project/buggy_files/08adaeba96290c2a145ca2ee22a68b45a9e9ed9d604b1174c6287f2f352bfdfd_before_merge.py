def user_exists(user,
                host='localhost',
                password=None,
                password_hash=None,
                passwordless=False,
                unix_socket=False,
                password_column=None,
                **connection_args):
    '''
    Checks if a user exists on the MySQL server. A login can be checked to see
    if passwordless login is permitted by omitting ``password`` and
    ``password_hash``, and using ``passwordless=True``.

    .. versionadded:: 0.16.2
        The ``passwordless`` option was added.

    CLI Example:

    .. code-block:: bash

        salt '*' mysql.user_exists 'username' 'hostname' 'password'
        salt '*' mysql.user_exists 'username' 'hostname' password_hash='hash'
        salt '*' mysql.user_exists 'username' passwordless=True
        salt '*' mysql.user_exists 'username' password_column='authentication_string'
    '''
    server_version = version(**connection_args)
    dbc = _connect(**connection_args)
    # Did we fail to connect with the user we are checking
    # Its password might have previously change with the same command/state
    if dbc is None \
            and __context__['mysql.error'] \
                .startswith("MySQL Error 1045: Access denied for user '{0}'@".format(user)) \
            and password:
        # Clear the previous error
        __context__['mysql.error'] = None
        connection_args['connection_pass'] = password
        dbc = _connect(**connection_args)
    if dbc is None:
        return False

    if not password_column:
        password_column = __password_column(**connection_args)

    cur = dbc.cursor()
    qry = ('SELECT User,Host FROM mysql.user WHERE User = %(user)s AND '
           'Host = %(host)s')
    args = {}
    args['user'] = user
    args['host'] = host

    if salt.utils.data.is_true(passwordless):
        if salt.utils.data.is_true(unix_socket):
            qry += ' AND plugin=%(unix_socket)s'
            args['unix_socket'] = 'unix_socket'
        else:
            qry += ' AND ' + password_column + ' = \'\''
    elif password:
        if salt.utils.versions.version_cmp(server_version, '8.0.11') <= 0:
            # Hash the password before comparing
            _password = __mysql_hash_password(password)
            qry += ' AND ' + password_column + ' = %(password)s'
        else:
            _password = password
            qry += ' AND ' + password_column + ' = PASSWORD(%(password)s)'
        args['password'] = six.text_type(_password)
    elif password_hash:
        qry += ' AND ' + password_column + ' = %(password)s'
        args['password'] = password_hash

    try:
        _execute(cur, qry, args)
    except MySQLdb.OperationalError as exc:
        err = 'MySQL Error {0}: {1}'.format(*exc)
        __context__['mysql.error'] = err
        log.error(err)
        return False

    return cur.rowcount == 1