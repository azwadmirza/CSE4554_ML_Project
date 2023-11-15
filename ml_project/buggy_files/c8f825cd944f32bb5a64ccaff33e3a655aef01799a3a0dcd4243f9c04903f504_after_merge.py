    def _key_deploy_run(self, host, target, re_run=True):
        '''
        The ssh-copy-id routine
        '''
        argv = [
            'ssh.set_auth_key',
            target.get('user', 'root'),
            self.get_pubkey(),
        ]

        single = Single(
                self.opts,
                argv,
                host,
                mods=self.mods,
                fsclient=self.fsclient,
                thin=self.thin,
                **target)
        if salt.utils.which('ssh-copy-id'):
            # we have ssh-copy-id, use it!
            stdout, stderr, retcode = single.shell.copy_id()
        else:
            stdout, stderr, retcode = single.run()
        if re_run:
            target.pop('passwd')
            single = Single(
                    self.opts,
                    self.opts['argv'],
                    host,
                    mods=self.mods,
                    fsclient=self.fsclient,
                    thin=self.thin,
                    **target)
            stdout, stderr, retcode = single.cmd_block()
            try:
                data = salt.utils.find_json(stdout)
                return {host: data.get('local', data)}
            except Exception:
                if stderr:
                    return {host: stderr}
                return {host: 'Bad Return'}
        if os.EX_OK != retcode:
            return {host: stderr}
        return {host: stdout}