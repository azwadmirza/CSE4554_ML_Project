    def _key_deploy_run(self, host, target, re_run=True):
        '''
        The ssh-copy-id routine
        '''
        arg_str = 'ssh.set_auth_key {0} {1}'.format(
                target.get('user', 'root'),
                self.get_pubkey())

        single = Single(
                self.opts,
                arg_str,
                host,
                **target)
        if salt.utils.which('ssh-copy-id'):
            # we have ssh-copy-id, use it!
            single.shell.copy_id()
        else:
            ret = single.run()
        if re_run:
            target.pop('passwd')
            single = Single(
                    self.opts,
                    self.opts['arg_str'],
                    host,
                    **target)
            stdout, stderr = single.cmd_block()
            try:
                data = json.loads(stdout)
                return {host: data.get('local', data)}
            except Exception:
                if stderr:
                    return {host: stderr}
                return {host: 'Bad Return'}