def user_chpass(user,
                host='localhost',
                password=None,
                password_hash=None,
                allow_passwordless=False,
                unix_socket=None,
                password_column=None,
                **connection_args):
    '''
    Change password for a MySQL user

    host
        Host for which this user/password combo applies

    password
        The password to set for the new user. Will take precedence over the
        ``password_hash`` option if both are specified.

    password_hash
        The password in hashed form. Be sure to quote the password because YAML
        doesn't like the ``*``. A password hash can be obtained from the mysql
        command-line client like so::

            mysql> SELECT PASSWORD('mypass');
            +-------------------------------------------+
            | PASSWORD('mypass')                        |
            +-------------------------------------------+
            | *6C8989366EAF75BB670AD8EA7A7FC1176A95CEF4 |
            +-------------------------------------------+
            1 row in set (0.00 sec)

    allow_passwordless
        If ``True``, then ``password`` and ``password_hash`` can be omitted (or
        set to ``None``) to permit a passwordless login.

    .. versionadded:: 0.16.2
        The ``allow_passwordless`` option was added.

    CLI Examples:

    .. code-block:: bash

        salt '*' mysql.user_chpass frank localhost newpassword
        salt '*' mysql.user_chpass frank localhost password_hash='hash'
        salt '*' mysql.user_chpass frank localhost allow_passwordless=True
    '''
    server_version = version(**connection_args)
    args = {}
    if password is not None:
        if salt.utils.versions.version_cmp(server_version, '8.0.11') <= 0:
            password_sql = '%(password)s'
        else:
            password_sql = 'PASSWORD(%(password)s)'
        args['password'] = password
    elif password_hash is not None:
        password_sql = '%(password)s'
        args['password'] = password_hash
    elif not salt.utils.data.is_true(allow_passwordless):
        log.error('password or password_hash must be specified, unless '
                  'allow_passwordless=True')
        return False
    else:
        password_sql = '\'\''

    dbc = _connect(**connection_args)
    if dbc is None:
        return False

    if not password_column:
        password_column = __password_column(**connection_args)

    cur = dbc.cursor()
    qry = ('UPDATE mysql.user SET ' + password_column + '='
           + password_sql +
           ' WHERE User=%(user)s AND Host = %(host)s;')
    args['user'] = user
    args['host'] = host
    if salt.utils.data.is_true(allow_passwordless) and \
            salt.utils.data.is_true(unix_socket):
        if host == 'localhost':
            qry = ('UPDATE mysql.user SET ' + password_column + '='
                   + password_sql + ', plugin=%(unix_socket)s' +
                   ' WHERE User=%(user)s AND Host = %(host)s;')
            args['unix_socket'] = 'unix_socket'
        else:
            log.error('Auth via unix_socket can be set only for host=localhost')
    try:
        result = _execute(cur, qry, args)
    except MySQLdb.OperationalError as exc:
        err = 'MySQL Error {0}: {1}'.format(*exc)
        __context__['mysql.error'] = err
        log.error(err)
        return False

    if result:
        _execute(cur, 'FLUSH PRIVILEGES;')
        log.info(
            'Password for user \'%s\'@\'%s\' has been %s',
                user, host,
                'changed' if any((password, password_hash)) else 'cleared'
        )
        return True

    log.info(
        'Password for user \'%s\'@\'%s\' was not %s',
            user, host,
            'changed' if any((password, password_hash)) else 'cleared'
    )
    return False