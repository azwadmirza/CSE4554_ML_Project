    def _run_command(self, host, command, sudo=False, user=None,
                     shell=None, use_shell=True, use_pty=True,
                     **paramiko_kwargs):
        """Make SSHClient, run command on host"""
        try:
            self._make_ssh_client(host, **paramiko_kwargs)
            return self.host_clients[host].exec_command(
                command, sudo=sudo, user=user, shell=shell,
                use_shell=use_shell, use_pty=use_pty)
        except Exception as ex:
            ex.host = host
            logger.error("Failed to run on host %s", host)
            raise ex