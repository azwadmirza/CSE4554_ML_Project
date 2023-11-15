    def _cmd_str(self, cmd, ssh='ssh'):
        '''
        Return the cmd string to execute
        '''

        # TODO: if tty, then our SSH_SHIM cannot be supplied from STDIN Will
        # need to deliver the SHIM to the remote host and execute it there

        if self.passwd and salt.utils.which('sshpass'):
            opts = self._passwd_opts()
            return 'sshpass -p "{0}" {1} {2} {3} {4} {5}'.format(
                    self.passwd,
                    ssh,
                    '' if ssh == 'scp' else self.host,
                    '-t -t' if self.tty else '',
                    opts,
                    cmd)
        if self.priv:
            opts = self._key_opts()
            return '{0} {1} {2} {3} {4}'.format(
                    ssh,
                    '' if ssh == 'scp' else self.host,
                    '-t -t' if self.tty else '',
                    opts,
                    cmd)
        return None