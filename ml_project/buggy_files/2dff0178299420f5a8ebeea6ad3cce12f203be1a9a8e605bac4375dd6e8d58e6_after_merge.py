    def run_command(self, command, user=None, stop_on_errors=True,
                    host_args=None, use_pty=False, shell=None,
                    encoding='utf-8', return_list=False,
                    *args, **kwargs):
        greenlet_timeout = kwargs.pop('greenlet_timeout', None)
        if host_args:
            try:
                cmds = [self.pool.spawn(self._run_command, host_i, host,
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
                self._run_command, host_i, host, command,
                user=user, encoding=encoding, use_pty=use_pty, shell=shell,
                *args, **kwargs)
                    for host_i, host in enumerate(self.hosts)]
        self.cmds = cmds
        joinall(cmds, raise_error=False, timeout=greenlet_timeout)
        if not return_list:
            warn(_output_depr_notice)
            output = {}
            return self._get_output_dict(
                cmds, output, stop_on_errors=stop_on_errors,
                timeout=greenlet_timeout)
        return [self._get_output_from_greenlet(cmd, timeout=greenlet_timeout)
                for cmd in cmds]