    def join(self, output, consume_output=False, timeout=None,
             encoding='utf-8'):
        """Wait until all remote commands in output have finished
        and retrieve exit codes. Does *not* block other commands from
        running in parallel.

        :param output: Output of commands to join on
        :type output: dict as returned by
          :py:func:`pssh.pssh_client.ParallelSSHClient.get_output`
        :param consume_output: Whether or not join should consume output
          buffers. Output buffers will be empty after ``join`` if set
          to ``True``. Must be set to ``True`` to allow host logger to log
          output on call to ``join`` when host logger has been enabled.
        :type consume_output: bool
        :param timeout: Timeout in seconds if remote command is not yet
          finished. Note that use of timeout forces ``consume_output=True``
          otherwise the channel output pending to be consumed always results
          in the channel not being finished.
        :type timeout: int
        :param encoding: Encoding to use for output. Must be valid
          `Python codec <https://docs.python.org/library/codecs.html>`_
        :type encoding: str

        :raises: :py:class:`pssh.exceptions.Timeout` on timeout requested and
          reached with commands still running.

        :rtype: ``None``"""
        cmds = []
        if isinstance(output, list):
            for host_i, host_out in enumerate(output):
                host = self.hosts[host_i]
                cmds.append(self.pool.spawn(
                    self._join, host_i, host, host_out,
                    consume_output=consume_output, timeout=timeout))
        elif isinstance(output, dict):
            for host_i, (host, host_out) in enumerate(output.items()):
                cmds.append(self.pool.spawn(
                    self._join, host_i, host, host_out,
                    consume_output=consume_output, timeout=timeout))
        else:
            raise ValueError("Unexpected output object type")
        # Errors raised by self._join should be propagated.
        # Timeouts are handled by self._join itself.
        joinall(cmds, raise_error=True)
        self.get_exit_codes(output)