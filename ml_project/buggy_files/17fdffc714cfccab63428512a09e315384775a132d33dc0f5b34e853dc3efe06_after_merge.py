    def prepare(self):
        '''
        Run the preparation sequence required to start a salt syndic minion.

        If sub-classed, don't **ever** forget to run:

            super(YourSubClass, self).prepare()
        '''
        super(Syndic, self).prepare()
        try:
            if self.config['verify_env']:
                verify_env(
                    [
                        self.config['pki_dir'],
                        self.config['cachedir'],
                        self.config['sock_dir'],
                        self.config['extension_modules'],
                    ],
                    self.config['user'],
                    permissive=self.config['permissive_pki_access'],
                    pki_dir=self.config['pki_dir'],
                )
                logfile = self.config['log_file']
                if logfile is not None and not logfile.startswith(('tcp://',
                                                                   'udp://',
                                                                   'file://')):
                    # Logfile is not using Syslog, verify
                    current_umask = os.umask(0o027)
                    verify_files([logfile], self.config['user'])
                    os.umask(current_umask)
        except OSError as err:
            log.exception('Failed to prepare salt environment')
            self.shutdown(err.errno)

        self.setup_logfile_logger()
        verify_log(self.config)
        log.info(
            'Setting up the Salt Syndic Minion "{0}"'.format(
                self.config['id']
            )
        )

        # Late import so logging works correctly
        import salt.minion
        self.daemonize_if_required()
        # if its a multisyndic, do so
        if isinstance(self.config.get('master'), list):
            self.syndic = salt.minion.MultiSyndic(self.config)
        else:
            self.syndic = salt.minion.Syndic(self.config)
        self.set_pidfile()