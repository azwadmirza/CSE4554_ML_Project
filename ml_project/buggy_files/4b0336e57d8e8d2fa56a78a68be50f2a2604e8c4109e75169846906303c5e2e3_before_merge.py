    def connect(self, **kwargs):
        host = self.module.params['host']
        port = self.module.params['port'] or 22

        username = self.module.params['username']
        password = self.module.params['password']
        key_filename = self.module.params['ssh_keyfile']
        timeout = self.module.params['timeout']

        try:
            self.shell = Shell(kickstart=False, prompts_re=CLI_PROMPTS_RE, errors_re=CLI_ERRORS_RE)
            self.shell.open(host, port=port, username=username, password=password, key_filename=key_filename, timeout=timeout)
        except ShellError:
            e = get_exception()
            msg = 'failed to connect to %s:%s - %s' % (host, port, str(e))
            self.module.fail_json(msg=msg)