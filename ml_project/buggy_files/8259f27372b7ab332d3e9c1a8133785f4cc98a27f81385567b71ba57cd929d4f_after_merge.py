    def _run_batch(self):
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
            try:
                batch = salt.cli.batch.Batch(self.config, eauth=eauth, parser=self.options)
            except salt.exceptions.SaltClientError as exc:
                # We will print errors to the console further down the stack
                sys.exit(1)
            # Printing the output is already taken care of in run() itself
            for res in batch.run():
                if self.options.failhard:
                    for ret in six.itervalues(res):
                        retcode = salt.utils.job.get_retcode(ret)
                        if retcode != 0:
                            sys.stderr.write('ERROR: Minions returned with non-zero exit code\n')
                            sys.exit(retcode)