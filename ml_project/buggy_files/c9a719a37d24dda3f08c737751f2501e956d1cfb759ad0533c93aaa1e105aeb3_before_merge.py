    def start(self, args):
        """Start Application."""
        app.instance = self
        signal.signal(signal.SIGINT, self.sig_handler)
        signal.signal(signal.SIGTERM, self.sig_handler)

        # do some preliminary stuff
        app.MY_FULLNAME = os.path.normpath(os.path.abspath(os.path.join(__file__, '..', '..', 'start.py')))
        app.MY_NAME = os.path.basename(app.MY_FULLNAME)
        app.PROG_DIR = os.path.dirname(app.MY_FULLNAME)
        app.DATA_DIR = app.PROG_DIR
        app.MY_ARGS = args

        try:
            locale.setlocale(locale.LC_ALL, '')
            app.SYS_ENCODING = locale.getpreferredencoding()
        except (locale.Error, IOError):
            app.SYS_ENCODING = 'UTF-8'

        # pylint: disable=no-member
        if (not app.SYS_ENCODING or
                app.SYS_ENCODING.lower() in ('ansi_x3.4-1968', 'us-ascii', 'ascii', 'charmap') or
                (sys.platform.startswith('win') and
                    sys.getwindowsversion()[0] >= 6 and
                    text_type(getattr(sys.stdout, 'device', sys.stdout).encoding).lower() in ('cp65001', 'charmap'))):
            app.SYS_ENCODING = 'UTF-8'

        # TODO: Continue working on making this unnecessary, this hack creates all sorts of hellish problems
        if not hasattr(sys, 'setdefaultencoding'):
            reload(sys)

        try:
            # On non-unicode builds this will raise an AttributeError, if encoding type is not valid it throws a LookupError
            sys.setdefaultencoding(app.SYS_ENCODING)  # pylint: disable=no-member
        except (AttributeError, LookupError):
            sys.exit('Sorry, you MUST add the Medusa folder to the PYTHONPATH environment variable or '
                     'find another way to force Python to use {encoding} for string encoding.'.format(encoding=app.SYS_ENCODING))

        self.console_logging = (not hasattr(sys, 'frozen')) or (app.MY_NAME.lower().find('-console') > 0)

        # Rename the main thread
        threading.currentThread().name = 'MAIN'

        try:
            opts, _ = getopt.getopt(
                args, 'hqdp::',
                ['help', 'quiet', 'nolaunch', 'daemon', 'pidfile=', 'port=', 'datadir=', 'config=', 'noresize']
            )
        except getopt.GetoptError:
            sys.exit(self.help_message())

        for option, value in opts:
            # Prints help message
            if option in ('-h', '--help'):
                sys.exit(self.help_message())

            # For now we'll just silence the logging
            if option in ('-q', '--quiet'):
                self.console_logging = False

            # Suppress launching web browser
            # Needed for OSes without default browser assigned
            # Prevent duplicate browser window when restarting in the app
            if option in ('--nolaunch',):
                self.no_launch = True

            # Override default/configured port
            if option in ('-p', '--port'):
                try:
                    self.forced_port = int(value)
                except ValueError:
                    sys.exit('Port: %s is not a number. Exiting.' % value)

            # Run as a double forked daemon
            if option in ('-d', '--daemon'):
                self.run_as_daemon = True
                # When running as daemon disable console_logging and don't start browser
                self.console_logging = False
                self.no_launch = True

                if sys.platform == 'win32' or sys.platform == 'darwin':
                    self.run_as_daemon = False

            # Write a pid file if requested
            if option in ('--pidfile',):
                self.create_pid = True
                self.pid_file = str(value)

                # If the pid file already exists, Medusa may still be running, so exit
                if os.path.exists(self.pid_file):
                    sys.exit('PID file: %s already exists. Exiting.' % self.pid_file)

            # Specify folder to load the config file from
            if option in ('--config',):
                app.CONFIG_FILE = os.path.abspath(value)

            # Specify folder to use as the data directory
            if option in ('--datadir',):
                app.DATA_DIR = os.path.abspath(value)

            # Prevent resizing of the banner/posters even if PIL is installed
            if option in ('--noresize',):
                app.NO_RESIZE = True

        # Keep backwards compatibility
        Application.backwards_compatibility()

        # The pid file is only useful in daemon mode, make sure we can write the file properly
        if self.create_pid:
            if self.run_as_daemon:
                pid_dir = os.path.dirname(self.pid_file)
                if not os.access(pid_dir, os.F_OK):
                    sys.exit('PID dir: %s doesn\'t exist. Exiting.' % pid_dir)
                if not os.access(pid_dir, os.W_OK):
                    sys.exit('PID dir: %s must be writable (write permissions). Exiting.' % pid_dir)

            else:
                if self.console_logging:
                    sys.stdout.write('Not running in daemon mode. PID file creation disabled.\n')

                self.create_pid = False

        # If they don't specify a config file then put it in the data dir
        if not app.CONFIG_FILE:
            app.CONFIG_FILE = os.path.join(app.DATA_DIR, 'config.ini')

        # Make sure that we can create the data dir
        if not os.access(app.DATA_DIR, os.F_OK):
            try:
                os.makedirs(app.DATA_DIR, 0o744)
            except os.error:
                raise SystemExit('Unable to create data directory: %s' % app.DATA_DIR)

        # Make sure we can write to the data dir
        if not os.access(app.DATA_DIR, os.W_OK):
            raise SystemExit('Data directory must be writeable: %s' % app.DATA_DIR)

        # Make sure we can write to the config file
        if not os.access(app.CONFIG_FILE, os.W_OK):
            if os.path.isfile(app.CONFIG_FILE):
                raise SystemExit('Config file must be writeable: %s' % app.CONFIG_FILE)
            elif not os.access(os.path.dirname(app.CONFIG_FILE), os.W_OK):
                raise SystemExit('Config file root dir must be writeable: %s' % os.path.dirname(app.CONFIG_FILE))

        os.chdir(app.DATA_DIR)

        # Check if we need to perform a restore first
        restore_dir = os.path.join(app.DATA_DIR, 'restore')
        if os.path.exists(restore_dir):
            success = self.restore_db(restore_dir, app.DATA_DIR)
            if self.console_logging:
                sys.stdout.write('Restore: restoring DB and config.ini %s!\n' % ('FAILED', 'SUCCESSFUL')[success])

        # Initialize all available themes
        app.AVAILABLE_THEMES = read_themes()
        app.DATA_ROOT = os.path.join(app.PROG_DIR, 'themes')

        # Load the config and publish it to the application package
        if self.console_logging and not os.path.isfile(app.CONFIG_FILE):
            sys.stdout.write('Unable to find %s, all settings will be default!\n' % app.CONFIG_FILE)

        app.CFG = ConfigObj(app.CONFIG_FILE, encoding='UTF-8', default_encoding='UTF-8')

        # Initialize the config and our threads
        self.initialize(console_logging=self.console_logging)

        if self.run_as_daemon:
            self.daemonize()

        # Get PID
        app.PID = os.getpid()

        # Build from the DB to start with
        self.load_shows_from_db()

        logger.info('Starting Medusa [{branch}] using {config!r}', branch=app.BRANCH, config=app.CONFIG_FILE)

        self.clear_cache()
        self.migrate_images()

        if self.forced_port:
            logger.info('Forcing web server to port {port}', port=self.forced_port)
            self.start_port = self.forced_port
        else:
            self.start_port = app.WEB_PORT

        if app.WEB_LOG:
            self.log_dir = app.LOG_DIR
        else:
            self.log_dir = None

        # app.WEB_HOST is available as a configuration value in various
        # places but is not configurable. It is supported here for historic reasons.
        if app.WEB_HOST and app.WEB_HOST != '0.0.0.0':
            self.web_host = app.WEB_HOST
        else:
            self.web_host = '' if app.WEB_IPV6 else '0.0.0.0'

        # web server options
        self.web_options = {
            'port': int(self.start_port),
            'host': self.web_host,
            'data_root': app.DATA_ROOT,
            'vue_root': os.path.join(app.PROG_DIR, 'vue'),
            'web_root': app.WEB_ROOT,
            'log_dir': self.log_dir,
            'username': app.WEB_USERNAME,
            'password': app.WEB_PASSWORD,
            'enable_https': app.ENABLE_HTTPS,
            'handle_reverse_proxy': app.HANDLE_REVERSE_PROXY,
            'https_cert': os.path.join(app.PROG_DIR, app.HTTPS_CERT),
            'https_key': os.path.join(app.PROG_DIR, app.HTTPS_KEY),
        }

        # start web server
        self.web_server = AppWebServer(self.web_options)
        self.web_server.start()

        # Fire up all our threads
        self.start_threads()

        # Build internal name cache
        name_cache.build_name_cache()

        # Pre-populate network timezones, it isn't thread safe
        network_timezones.update_network_dict()

        # # why???
        # if app.USE_FAILED_DOWNLOADS:
        #     failed_history.trim_history()

        # # Check for metadata indexer updates for shows (Disabled until we use api)
        # app.show_update_scheduler.forceRun()

        # Launch browser
        if app.LAUNCH_BROWSER and not (self.no_launch or self.run_as_daemon):
            Application.launch_browser('https' if app.ENABLE_HTTPS else 'http', self.start_port, app.WEB_ROOT)

        # main loop
        while app.started:
            time.sleep(1)