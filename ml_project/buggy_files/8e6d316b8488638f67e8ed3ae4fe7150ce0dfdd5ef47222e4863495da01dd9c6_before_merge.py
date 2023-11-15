    def join_shells(self, shells, timeout=None):
        """Wait for running commands to complete and close shells.

        :param shells: Shells to join on.
        :type shells: list(:py:class:`pssh.clients.base.single.InteractiveShell`)
        :param timeout: Seconds before waiting for shell commands to finish times out.
          Defaults to self.timeout if not provided.
        :type timeout: float

        :raises: :py:class:`pssh.exceptions.Timeout` on timeout requested and
          reached with commands still running.
        """
        _timeout = self.timeout if timeout is None else timeout
        cmds = [self.pool.spawn(shell.close) for shell in shells]
        finished = joinall(cmds, timeout=_timeout)
        if _timeout is None:
            return
        finished_shells = [g.get() for g in finished]
        unfinished_shells = list(set(shells).difference(set(finished_shells)))
        if len(unfinished_shells) > 0:
            raise Timeout("Timeout of %s sec(s) reached with commands "
                          "still running", timeout, finished_shells, unfinished_shells)