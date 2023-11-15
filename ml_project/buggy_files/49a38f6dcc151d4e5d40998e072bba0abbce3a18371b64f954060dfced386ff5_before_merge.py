def _connect(**kwargs):
    '''
    wrap authentication credentials here
    '''
    connargs = dict()

    def _connarg(name, key=None, get_opts=True):
        '''
        Add key to connargs, only if name exists in our kwargs or,
        if get_opts is true, as mysql.<name> in __opts__ or __pillar__

        If get_opts is true, evaluate in said order - kwargs, opts
        then pillar. To avoid collision with other functions,
        kwargs-based connection arguments are prefixed with 'connection_'
        (i.e. 'connection_host', 'connection_user', etc.).
        '''
        if key is None:
            key = name

        if name in kwargs:
            connargs[key] = kwargs[name]
        elif get_opts:
            prefix = 'connection_'
            if name.startswith(prefix):
                try:
                    name = name[len(prefix):]
                except IndexError:
                    return
            val = __salt__['config.option']('mysql.{0}'.format(name), None)
            if val is not None:
                connargs[key] = val

    # If a default file is explicitly passed to kwargs, don't grab the
    # opts/pillar settings, as it can override info in the defaults file
    if 'connection_default_file' in kwargs:
        get_opts = False
    else:
        get_opts = True

    _connarg('connection_host', 'host', get_opts)
    _connarg('connection_user', 'user', get_opts)
    _connarg('connection_pass', 'passwd', get_opts)
    _connarg('connection_port', 'port', get_opts)
    _connarg('connection_db', 'db', get_opts)
    _connarg('connection_conv', 'conv', get_opts)
    _connarg('connection_unix_socket', 'unix_socket', get_opts)
    _connarg('connection_default_file', 'read_default_file', get_opts)
    _connarg('connection_default_group', 'read_default_group', get_opts)
    # MySQLdb states that this is required for charset usage
    # but in fact it's more than it's internally activated
    # when charset is used, activating use_unicode here would
    # retrieve utf8 strings as unicode() objects in salt
    # and we do not want that.
    #_connarg('connection_use_unicode', 'use_unicode')
    connargs['use_unicode'] = False
    _connarg('connection_charset', 'charset')
    # Ensure MySQldb knows the format we use for queries with arguments
    MySQLdb.paramstyle = 'pyformat'

    try:
        dbc = MySQLdb.connect(**connargs)
    except MySQLdb.OperationalError as exc:
        err = 'MySQL Error {0}: {1}'.format(*exc)
        __context__['mysql.error'] = err
        log.error(err)
        return None

    dbc.autocommit(True)
    return dbc