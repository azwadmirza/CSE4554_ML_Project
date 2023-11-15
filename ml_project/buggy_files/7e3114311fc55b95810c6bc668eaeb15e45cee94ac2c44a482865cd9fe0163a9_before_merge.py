    def __init__(self, host="localhost", user=None, password="",
                 db=None, port=3306, unix_socket=None,
                 charset='', sql_mode=None,
                 read_default_file=None, conv=decoders, use_unicode=None,
                 client_flag=0, cursorclass=Cursor, init_command=None,
                 connect_timeout=None, read_default_group=None,
                 no_delay=None, autocommit=False, echo=False,
                 local_infile=False, loop=None, ssl=None, auth_plugin='',
                 program_name=''):
        """
        Establish a connection to the MySQL database. Accepts several
        arguments:

        :param host: Host where the database server is located
        :param user: Username to log in as
        :param password: Password to use.
        :param db: Database to use, None to not use a particular one.
        :param port: MySQL port to use, default is usually OK.
        :param unix_socket: Optionally, you can use a unix socket rather
        than TCP/IP.
        :param charset: Charset you want to use.
        :param sql_mode: Default SQL_MODE to use.
        :param read_default_file: Specifies  my.cnf file to read these
            parameters from under the [client] section.
        :param conv: Decoders dictionary to use instead of the default one.
            This is used to provide custom marshalling of types.
            See converters.
        :param use_unicode: Whether or not to default to unicode strings.
        :param  client_flag: Custom flags to send to MySQL. Find
            potential values in constants.CLIENT.
        :param cursorclass: Custom cursor class to use.
        :param init_command: Initial SQL statement to run when connection is
            established.
        :param connect_timeout: Timeout before throwing an exception
            when connecting.
        :param read_default_group: Group to read from in the configuration
            file.
        :param no_delay: Disable Nagle's algorithm on the socket
        :param autocommit: Autocommit mode. None means use server default.
            (default: False)
        :param local_infile: boolean to enable the use of LOAD DATA LOCAL
            command. (default: False)
        :param ssl: Optional SSL Context to force SSL
        :param auth_plugin: String to manually specify the authentication
            plugin to use, i.e you will want to use mysql_clear_password
            when using IAM authentication with Amazon RDS.
            (default: Server Default)
        :param program_name: Program name string to provide when
            handshaking with MySQL. (default: sys.argv[0])
        :param loop: asyncio loop
        """
        self._loop = loop or asyncio.get_event_loop()

        if use_unicode is None and sys.version_info[0] > 2:
            use_unicode = True

        if read_default_file:
            if not read_default_group:
                read_default_group = "client"
            cfg = configparser.RawConfigParser()
            cfg.read(os.path.expanduser(read_default_file))
            _config = partial(cfg.get, read_default_group)

            user = _config("user", fallback=user)
            password = _config("password", fallback=password)
            host = _config("host", fallback=host)
            db = _config("database", fallback=db)
            unix_socket = _config("socket", fallback=unix_socket)
            port = int(_config("port", fallback=port))
            charset = _config("default-character-set", fallback=charset)

        # pymysql port
        if no_delay is not None:
            warnings.warn("no_delay option is deprecated", DeprecationWarning)
            no_delay = bool(no_delay)
        else:
            no_delay = True

        self._host = host
        self._port = port
        self._user = user or DEFAULT_USER
        self._password = password or ""
        self._db = db
        self._no_delay = no_delay
        self._echo = echo
        self._last_usage = self._loop.time()
        self._client_auth_plugin = auth_plugin
        self._server_auth_plugin = ""
        self._auth_plugin_used = ""

        # TODO somehow import version from __init__.py
        self._connect_attrs = {
            '_client_name': 'aiomysql',
            '_pid': str(os.getpid()),
            '_client_version': '0.0.16',
        }
        if program_name:
            self._connect_attrs["program_name"] = program_name
        elif sys.argv:
            self._connect_attrs["program_name"] = sys.argv[0]

        self._unix_socket = unix_socket
        if charset:
            self._charset = charset
            self.use_unicode = True
        else:
            self._charset = DEFAULT_CHARSET
            self.use_unicode = False

        if use_unicode is not None:
            self.use_unicode = use_unicode

        self._ssl_context = ssl
        if ssl:
            client_flag |= CLIENT.SSL

        self._encoding = charset_by_name(self._charset).encoding

        if local_infile:
            client_flag |= CLIENT.LOCAL_FILES

        client_flag |= CLIENT.CAPABILITIES
        client_flag |= CLIENT.MULTI_STATEMENTS
        if self._db:
            client_flag |= CLIENT.CONNECT_WITH_DB
        self.client_flag = client_flag

        self.cursorclass = cursorclass
        self.connect_timeout = connect_timeout

        self._result = None
        self._affected_rows = 0
        self.host_info = "Not connected"

        #: specified autocommit mode. None means use server default.
        self.autocommit_mode = autocommit

        self.encoders = encoders  # Need for MySQLdb compatibility.
        self.decoders = conv
        self.sql_mode = sql_mode
        self.init_command = init_command

        # asyncio StreamReader, StreamWriter
        self._reader = None
        self._writer = None
        # If connection was closed for specific reason, we should show that to
        # user
        self._close_reason = None