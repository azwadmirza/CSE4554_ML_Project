    def _run_command(self, host_i, host, command, sudo=False, user=None,
                     shell=None, use_pty=False,
                     encoding='utf-8', timeout=None):
        """Make SSHClient if needed, run command on host"""
        try:
            self._make_ssh_client(host_i, host)
            return self._host_clients[(host_i, host)].run_command(
                command, sudo=sudo, user=user, shell=shell,
                use_pty=use_pty, encoding=encoding, timeout=timeout)
        except Exception as ex:
            ex.host = host
            logger.error("Failed to run on host %s - %s", host, ex)
            raise ex