def connect(host="localhost", user=None, password="",
            db=None, port=3306, unix_socket=None,
            charset='', sql_mode=None,
            read_default_file=None, conv=decoders, use_unicode=None,
            client_flag=0, cursorclass=Cursor, init_command=None,
            connect_timeout=None, read_default_group=None,
            no_delay=None, autocommit=False, echo=False,
            local_infile=False, loop=None, ssl=None, auth_plugin='',
            program_name=''):
    """See connections.Connection.__init__() for information about
    defaults."""
    coro = _connect(host=host, user=user, password=password, db=db,
                    port=port, unix_socket=unix_socket, charset=charset,
                    sql_mode=sql_mode, read_default_file=read_default_file,
                    conv=conv, use_unicode=use_unicode,
                    client_flag=client_flag, cursorclass=cursorclass,
                    init_command=init_command,
                    connect_timeout=connect_timeout,
                    read_default_group=read_default_group,
                    no_delay=no_delay, autocommit=autocommit, echo=echo,
                    local_infile=local_infile, loop=loop, ssl=ssl,
                    auth_plugin=auth_plugin, program_name=program_name)
    return _ConnectionContextManager(coro)