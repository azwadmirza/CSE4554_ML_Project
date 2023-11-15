    def join(self, output, consume_output=False, timeout=None, encoding='utf-8'):
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

        :raises: :py:class:`pssh.exceptions.Timeout` on timeout requested and
          reached with commands still running.

        :rtype: ``None``"""
        for host, host_out in output.items():
            if host not in self.host_clients or self.host_clients[host] is None:
                continue
            client = self.host_clients[host]
            channel = host_out.channel
            stdout, stderr = self.reset_output_generators(
                host_out, client=client, channel=channel, timeout=timeout, encoding=encoding)
            try:
                client.wait_finished(channel, timeout=timeout)
            except Timeout:
                raise Timeout(
                    "Timeout of %s sec(s) reached on host %s with command "
                    "still running", timeout, host)
            if timeout:
                # Must consume buffers prior to EOF check
                self._consume_output(stdout, stderr)
                if not channel.eof():
                    raise Timeout(
                        "Timeout of %s sec(s) reached on host %s with command "
                        "still running", timeout, host)
            elif consume_output:
                self._consume_output(stdout, stderr)
        self.get_exit_codes(output)