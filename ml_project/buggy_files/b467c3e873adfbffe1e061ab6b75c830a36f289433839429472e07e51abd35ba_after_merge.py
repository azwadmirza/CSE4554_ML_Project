def user_create(user,
                host='localhost',
                password=None,
                password_hash=None,
                allow_passwordless=False,
                unix_socket=False,
                password_column=None,
                **connection_args):
    '''
    Creates a MySQL user

    host
        Host for which this user/password combo applies

    password
        The password to use for the new user. Will take precedence over the
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

    unix_socket
        If ``True`` and allow_passwordless is ``True`` then will be used unix_socket auth plugin.

    .. versionadded:: 0.16.2
        The ``allow_passwordless`` option was added.

    CLI Examples:

    .. code-block:: bash

        salt '*' mysql.user_create 'username' 'hostname' 'password'
        salt '*' mysql.user_create 'username' 'hostname' password_hash='hash'
        salt '*' mysql.user_create 'username' 'hostname' allow_passwordless=True
    '''
    server_version = version(**connection_args)
    compare_version = '10.2.0' if 'MariaDB' in server_version else '8.0.11'
    if user_exists(user, host, **connection_args):
        log.info('User \'%s\'@\'%s\' already exists', user, host)
        return False

    dbc = _connect(**connection_args)
    if dbc is None:
        return False

    if not password_column:
        password_column = __password_column(**connection_args)

    cur = dbc.cursor()
    qry = 'CREATE USER %(user)s@%(host)s'
    args = {}
    args['user'] = user
    args['host'] = host
    if password is not None:
        qry += ' IDENTIFIED BY %(password)s'
        args['password'] = six.text_type(password)
    elif password_hash is not None:
        if salt.utils.versions.version_cmp(server_version, compare_version) >= 0:
            qry += ' IDENTIFIED BY %(password)s'
        else:
            qry += ' IDENTIFIED BY PASSWORD %(password)s'
        args['password'] = password_hash
    elif salt.utils.data.is_true(allow_passwordless):
        if salt.utils.data.is_true(unix_socket):
            if host == 'localhost':
                qry += ' IDENTIFIED VIA unix_socket'
            else:
                log.error(
                    'Auth via unix_socket can be set only for host=localhost'
                )
    else:
        log.error('password or password_hash must be specified, unless '
                  'allow_passwordless=True')
        return False

    try:
        _execute(cur, qry, args)
    except MySQLdb.OperationalError as exc:
        err = 'MySQL Error {0}: {1}'.format(*exc.args)
        __context__['mysql.error'] = err
        log.error(err)
        return False

    if user_exists(user, host, password, password_hash, password_column=password_column, **connection_args):
        msg = 'User \'{0}\'@\'{1}\' has been created'.format(user, host)
        if not any((password, password_hash)):
            msg += ' with passwordless login'
        log.info(msg)
        return True

    log.info('User \'%s\'@\'%s\' was not created', user, host)
    return False