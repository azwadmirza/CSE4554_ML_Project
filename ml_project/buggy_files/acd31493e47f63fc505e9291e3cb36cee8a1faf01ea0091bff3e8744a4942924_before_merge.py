    def run(self):
        '''
        Execute the salt command line
        '''
        import salt.auth
        import salt.client
        self.parse_args()

        if self.config['verify_env']:
            if not self.config['log_file'].startswith(('tcp://',
                                                       'udp://',
                                                       'file://')):
                # Logfile is not using Syslog, verify
                verify_files(
                    [self.config['log_file']],
                    self.config['user']
                )

        # Setup file logging!
        self.setup_logfile_logger()

        try:
            # We don't need to bail on config file permission errors
            # if the CLI
            # process is run with the -a flag
            skip_perm_errors = self.options.eauth != ''

            local = salt.client.get_local_client(
                self.get_config_file_path(),
                skip_perm_errors=skip_perm_errors)
        except SaltClientError as exc:
            self.exit(2, '{0}\n'.format(exc))
            return

        if self.options.batch or self.options.static:
            import salt.cli.batch
            eauth = {}
            if 'token' in self.config:
                eauth['token'] = self.config['token']

            # If using eauth and a token hasn't already been loaded into
            # kwargs, prompt the user to enter auth credentials
            if 'token' not in eauth and self.options.eauth:
                resolver = salt.auth.Resolver(self.config)
                res = resolver.cli(self.options.eauth)
                if self.options.mktoken and res:
                    tok = resolver.token_cli(
                            self.options.eauth,
                            res
                            )
                    if tok:
                        eauth['token'] = tok.get('token', '')
                if not res:
                    sys.stderr.write('ERROR: Authentication failed\n')
                    sys.exit(2)
                eauth.update(res)
                eauth['eauth'] = self.options.eauth

            if self.options.static:

                if not self.options.batch:
                    self.config['batch'] = '100%'

                batch = salt.cli.batch.Batch(self.config, eauth=eauth, quiet=True)

                ret = {}

                for res in batch.run():
                    ret.update(res)

                self._output_ret(ret, '')

            else:
                batch = salt.cli.batch.Batch(self.config, eauth=eauth)
                # Printing the output is already taken care of in run() itself
                for res in batch.run():
                    if self.options.failhard:
                        for ret in res.itervalues():
                            retcode = salt.utils.job.get_retcode(ret)
                            if retcode != 0:
                                sys.stderr.write('ERROR: Minions returned with non-zero exit code\n')
                                sys.exit(retcode)

        else:
            if self.options.timeout <= 0:
                self.options.timeout = local.opts['timeout']

            kwargs = {
                'tgt': self.config['tgt'],
                'fun': self.config['fun'],
                'arg': self.config['arg'],
                'timeout': self.options.timeout,
                'show_timeout': self.options.show_timeout,
                'show_jid': self.options.show_jid}

            if 'token' in self.config:
                try:
                    with salt.utils.fopen(os.path.join(self.config['cachedir'], '.root_key'), 'r') as fp_:
                        kwargs['key'] = fp_.readline()
                except IOError:
                    kwargs['token'] = self.config['token']

            kwargs['delimiter'] = self.options.delimiter

            if self.selected_target_option:
                kwargs['expr_form'] = self.selected_target_option
            else:
                kwargs['expr_form'] = 'glob'

            if getattr(self.options, 'return'):
                kwargs['ret'] = getattr(self.options, 'return')

            if getattr(self.options, 'return_config'):
                kwargs['ret_config'] = getattr(self.options, 'return_config')

            if getattr(self.options, 'metadata'):
                kwargs['metadata'] = getattr(self.options, 'metadata')

            # If using eauth and a token hasn't already been loaded into
            # kwargs, prompt the user to enter auth credentials
            if 'token' not in kwargs and self.options.eauth:
                resolver = salt.auth.Resolver(self.config)
                res = resolver.cli(self.options.eauth)
                if self.options.mktoken and res:
                    tok = resolver.token_cli(
                            self.options.eauth,
                            res
                            )
                    if tok:
                        kwargs['token'] = tok.get('token', '')
                if not res:
                    sys.stderr.write('ERROR: Authentication failed\n')
                    sys.exit(2)
                kwargs.update(res)
                kwargs['eauth'] = self.options.eauth

            if self.config['async']:
                jid = local.cmd_async(**kwargs)
                print_cli('Executed command with job ID: {0}'.format(jid))
                return
            retcodes = []
            try:
                # local will be None when there was an error
                errors = []
                if local:
                    if self.options.subset:
                        cmd_func = local.cmd_subset
                        kwargs['sub'] = self.options.subset
                        kwargs['cli'] = True
                    else:
                        cmd_func = local.cmd_cli

                    if self.options.progress:
                        kwargs['progress'] = True
                        self.config['progress'] = True
                        ret = {}
                        for progress in cmd_func(**kwargs):
                            out = 'progress'
                            self._progress_ret(progress, out)
                            if 'return_count' not in progress:
                                ret.update(progress)
                        self._progress_end(out)
                        self._print_returns_summary(ret)
                    elif self.config['fun'] == 'sys.doc':
                        ret = {}
                        out = ''
                        for full_ret in local.cmd_cli(**kwargs):
                            ret_, out, retcode = self._format_ret(full_ret)
                            ret.update(ret_)
                        self._output_ret(ret, out)
                    else:
                        if self.options.verbose:
                            kwargs['verbose'] = True
                        ret = {}
                        for full_ret in cmd_func(**kwargs):
                            try:
                                ret_, out, retcode = self._format_ret(full_ret)
                                retcodes.append(retcode)
                                self._output_ret(ret_, out)
                                ret.update(ret_)
                            except KeyError:
                                errors.append(full_ret)

                    # Returns summary
                    if self.config['cli_summary'] is True:
                        if self.config['fun'] != 'sys.doc':
                            if self.options.output is None:
                                self._print_returns_summary(ret)
                                self._print_errors_summary(errors)

                    # NOTE: Return code is set here based on if all minions
                    # returned 'ok' with a retcode of 0.
                    # This is the final point before the 'salt' cmd returns,
                    # which is why we set the retcode here.
                    if retcodes.count(0) < len(retcodes):
                        sys.stderr.write('ERROR: Minions returned with non-zero exit code\n')
                        sys.exit(11)

            except (SaltInvocationError, EauthAuthenticationError, SaltClientError) as exc:
                ret = str(exc)
                out = ''
                self._output_ret(ret, out)