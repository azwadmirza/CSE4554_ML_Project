    def prepare(self):
        '''
        Run the preparation sequence required to start a salt proxy minion.

        If sub-classed, don't **ever** forget to run:

            super(YourSubClass, self).prepare()
        '''
        super(ProxyMinion, self).prepare()

        if not self.values.proxyid:
            self.error('salt-proxy requires --proxyid')

        # Proxies get their ID from the command line.  This may need to change in
        # the future.
        # We used to set this here.  Now it is set in ProxyMinionOptionParser
        # by passing it via setup_config to config.minion_config
        # self.config['id'] = self.values.proxyid

        try:
            if self.config['verify_env']:
                confd = self.config.get('default_include')
                if confd:
                    # If 'default_include' is specified in config, then use it
                    if '*' in confd:
                        # Value is of the form "minion.d/*.conf"
                        confd = os.path.dirname(confd)
                    if not os.path.isabs(confd):
                        # If configured 'default_include' is not an absolute
                        # path, consider it relative to folder of 'conf_file'
                        # (/etc/salt by default)
                        confd = os.path.join(
                            os.path.dirname(self.config['conf_file']), confd
                        )
                else:
                    confd = os.path.join(
                        os.path.dirname(self.config['conf_file']), 'proxy.d'
                    )

                v_dirs = [
                    self.config['pki_dir'],
                    self.config['cachedir'],
                    self.config['sock_dir'],
                    self.config['extension_modules'],
                    confd,
                ]

                if self.config.get('transport') == 'raet':
                    v_dirs.append(os.path.join(self.config['pki_dir'], 'accepted'))
                    v_dirs.append(os.path.join(self.config['pki_dir'], 'pending'))
                    v_dirs.append(os.path.join(self.config['pki_dir'], 'rejected'))
                    v_dirs.append(os.path.join(self.config['cachedir'], 'raet'))

                verify_env(
                    v_dirs,
                    self.config['user'],
                    permissive=self.config['permissive_pki_access'],
                    pki_dir=self.config['pki_dir'],
                )
        except OSError as error:
            self.environment_failure(error)

        self.setup_logfile_logger()
        verify_log(self.config)
        self.action_log_info('Setting up "{0}"'.format(self.config['id']))

        migrations.migrate_paths(self.config)

        # Bail out if we find a process running and it matches out pidfile
        if self.check_running():
            self.action_log_info('An instance is already running. Exiting')
            self.shutdown(1)

        # TODO: AIO core is separate from transport
        if self.config['transport'].lower() in ('zeromq', 'tcp', 'detect'):
            # Late import so logging works correctly
            import salt.minion
            # If the minion key has not been accepted, then Salt enters a loop
            # waiting for it, if we daemonize later then the minion could halt
            # the boot process waiting for a key to be accepted on the master.
            # This is the latest safe place to daemonize
            self.daemonize_if_required()
            self.set_pidfile()
            if self.config.get('master_type') == 'func':
                salt.minion.eval_master_func(self.config)
            self.minion = salt.minion.ProxyMinionManager(self.config)
        else:
            # For proxy minions, this doesn't work yet.
            import salt.daemons.flo
            self.daemonize_if_required()
            self.set_pidfile()
            self.minion = salt.daemons.flo.IofloMinion(self.config)