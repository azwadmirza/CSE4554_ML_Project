    def join(self, output=None, consume_output=False, timeout=None,
             encoding='utf-8'):
        """Wait until all remote commands in output have finished.
        Does *not* block other commands from running in parallel.

        :param output: Output of commands to join on
        :type output: `HostOutput` objects
        :param consume_output: Whether or not join should consume output
          buffers. Output buffers will be empty after ``join`` if set
          to ``True``. Must be set to ``True`` to allow host logger to log
          output on call to ``join`` when host logger has been enabled.
        :type consume_output: bool
        :param timeout: Timeout in seconds if **all** remote commands are not
          yet finished.
          This function's timeout is for all commands in total and will therefor
          be affected by pool size and total number of concurrent commands in
          self.pool.
          Since self.timeout is passed onto each individual SSH session it is
          **not** used for any parallel functions like `run_command` or `join`.
        :type timeout: int
        :param encoding: Unused - encoding from each ``HostOutput`` is used instead.
          To be removed in future releases.
        :type encoding: str

        :raises: :py:class:`pssh.exceptions.Timeout` on timeout requested and
          reached with commands still running.

        :rtype: ``None``"""
        if output is None:
            output = self.get_last_output()
        elif not isinstance(output, list):
            raise ValueError("Unexpected output object type")
        cmds = [self.pool.spawn(self._join, host_out, timeout=timeout,
                                consume_output=consume_output, encoding=encoding)
                for host_i, host_out in enumerate(output)]
        # Errors raised by self._join should be propagated.
        finished_cmds = joinall(cmds, raise_error=True, timeout=timeout)
        if timeout is None:
            return
        unfinished_cmds = set.difference(set(cmds), set(finished_cmds))
        if unfinished_cmds:
            finished_output = self.get_last_output(cmds=finished_cmds)
            unfinished_output = list(set.difference(set(output), set(finished_output)))
            raise Timeout("Timeout of %s sec(s) reached with commands "
                          "still running", timeout, finished_output, unfinished_output)