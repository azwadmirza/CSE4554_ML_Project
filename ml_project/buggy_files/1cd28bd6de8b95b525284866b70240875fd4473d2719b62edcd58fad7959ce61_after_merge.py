    def start(self):
        """
        Starting point when executing from commandline, dispatch execution to correct destination.

        If there is a FlexGet process with an ipc server already running, the command will be sent there for execution
        and results will be streamed back.
        If not, this will attempt to obtain a lock, initialize the manager, and run the command here.
        """
        # When we are in test mode, we use a different lock file and db
        if self.options.test:
            self.lockfile = os.path.join(self.config_base, '.test-%s-lock' % self.config_name)
        # If another process is started, send the execution to the running process
        ipc_info = self.check_ipc_info()
        if ipc_info:
            console('There is a FlexGet process already running for this config, sending execution there.')
            log.debug('Sending command to running FlexGet process: %s' % self.args)
            try:
                client = IPCClient(ipc_info['port'], ipc_info['password'])
            except ValueError as e:
                log.error(e)
            else:
                try:
                    client.handle_cli(self.args)
                except KeyboardInterrupt:
                    log.error('Disconnecting from daemon due to ctrl-c. Executions will still continue in the '
                              'background.')
                except EOFError:
                    log.error('Connection from daemon was severed.')
            return
        if self.options.test:
            log.info('Test mode, creating a copy from database ...')
            db_test_filename = os.path.join(self.config_base, 'test-%s.sqlite' % self.config_name)
            if os.path.exists(self.db_filename):
                shutil.copy(self.db_filename, db_test_filename)
                log.info('Test database created')
            self.db_filename = db_test_filename
        # No running process, we start our own to handle command
        with self.acquire_lock():
            self.initialize()
            self.handle_cli()
            self._shutdown()