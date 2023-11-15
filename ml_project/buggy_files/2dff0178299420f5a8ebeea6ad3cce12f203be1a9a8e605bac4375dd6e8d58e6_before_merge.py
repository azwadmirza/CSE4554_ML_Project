    def run_command(self, command, user=None, stop_on_errors=True,
                    host_args=None, use_pty=False, shell=None,
                    encoding='utf-8',
                    *args, **kwargs):
        greenlet_timeout = kwargs.pop('greenlet_timeout', None)
        output = {}
        if host_args:
            try:
                cmds = [self.pool.spawn(self._run_command, host,
                                        command % host_args[host_i],
                                        user=user, encoding=encoding,
                                        use_pty=use_pty, shell=shell,
                                        *args, **kwargs)
                        for host_i, host in enumerate(self.hosts)]
            except IndexError:
                raise HostArgumentException(
                    "Number of host arguments provided does not match "
                    "number of hosts ")
        else:
            cmds = [self.pool.spawn(
                self._run_command, host, command,
                user=user, encoding=encoding, use_pty=use_pty, shell=shell,
                *args, **kwargs)
                    for host in self.hosts]
        for cmd in cmds:
            try:
                self.get_output(cmd, output, timeout=greenlet_timeout)
            except Exception:
                if stop_on_errors:
                    raise
        self.cmds = cmds
        return output