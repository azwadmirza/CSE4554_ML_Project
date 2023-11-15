    def get_output(self, cmd, output, timeout=None):
        """Get output from command.

        :param output: Dictionary containing
          :py:class:`pssh.output.HostOutput` values to be updated with output
          from cmd
        :type output: dict
        :rtype: None
        """
        warn(_get_output_depr_notice)
        if not isinstance(output, dict):
            raise ValueError(
                "get_output is for the deprecated dictionary output only. "
                "To be removed in 2.0.0")
        try:
            (channel, host, stdout, stderr, stdin) = cmd.get(timeout=timeout)
        except Exception as ex:
            host = ex.host
            self._update_host_output(
                output, host, None, None, None, None, None, cmd, exception=ex)
            raise
        self._update_host_output(output, host, self._get_exit_code(channel),
                                 channel, stdout, stderr, stdin, cmd)