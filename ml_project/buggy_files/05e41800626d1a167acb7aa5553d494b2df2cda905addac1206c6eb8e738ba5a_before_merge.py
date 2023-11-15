    def __init__(self, args):
        """
        :param args: CLI args
        """
        global manager
        if not self.unit_test:
            assert not manager, 'Only one instance of Manager should be created at a time!'
        elif manager:
            log.info('last manager was not torn down correctly')

        if args is None:
            # Decode all arguments to unicode before parsing
            args = unicode_argv()[1:]
        self.args = args
        self.autoreload_config = False
        self.config_file_hash = None
        self.config_base = None
        self.config_name = None
        self.config_path = None
        self.db_filename = None
        self.engine = None
        self.lockfile = None
        self.database_uri = None
        self.db_upgraded = False
        self._has_lock = False
        self.is_daemon = False
        self.ipc_server = None
        self.task_queue = None
        self.persist = None
        self.initialized = False

        self.config = {}

        if '--help' in args or '-h' in args:
            # TODO: This is a bit hacky, but we can't call parse on real arguments when --help is used because it will
            # cause a system exit before plugins are loaded and print incomplete help. This will get us a default
            # options object and we'll parse the real args later, or send them to daemon. #2807
            self.options, _ = CoreArgumentParser().parse_known_args(['execute'])
        else:
            try:
                self.options, _ = CoreArgumentParser().parse_known_args(args)
            except ParserError:
                try:
                    # If a non-built-in command was used, we need to parse with a parser that
                    # doesn't define the subparsers
                    self.options, _ = manager_parser.parse_known_args(args)
                except ParserError as e:
                    manager_parser.print_help()
                    print('\nError: %s' % e.message)
                    sys.exit(1)
        try:
            self.find_config(create=False)
        except:
            logger.start(level=self.options.loglevel.upper(), to_file=False)
            raise
        else:
            log_file = os.path.expanduser(self.options.logfile)
            # If an absolute path is not specified, use the config directory.
            if not os.path.isabs(log_file):
                log_file = os.path.join(self.config_base, log_file)

            logger.start(log_file, self.options.loglevel.upper(), to_console=not self.options.cron)

        manager = self

        log.debug('sys.defaultencoding: %s' % sys.getdefaultencoding())
        log.debug('sys.getfilesystemencoding: %s' % sys.getfilesystemencoding())
        log.debug('os.path.supports_unicode_filenames: %s' % os.path.supports_unicode_filenames)
        if codecs.lookup(sys.getfilesystemencoding()).name == 'ascii' and not os.path.supports_unicode_filenames:
            log.warning('Your locale declares ascii as the filesystem encoding. Any plugins reading filenames from '
                        'disk will not work properly for filenames containing non-ascii characters. Make sure your '
                        'locale env variables are set up correctly for the environment which is launching FlexGet.')