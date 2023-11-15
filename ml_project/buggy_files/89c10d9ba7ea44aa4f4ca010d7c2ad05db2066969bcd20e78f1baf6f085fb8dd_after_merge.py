    def reset_output_generators(self, host_out, timeout=None,
                                client=None, channel=None,
                                encoding='utf-8'):
        """Reset output generators for host output. This creates new
        generators for stdout and stderr for the provided host output, useful
        in cases where the previous generators have raised a Timeout but the
        remote command is still running.

        :param host_out: Host output
        :type host_out: :py:class:`pssh.output.HostOutput`
        :param client: (Optional) SSH client
        :type client: :py:class:`pssh.ssh2_client.SSHClient`
        :param channel: (Optional) SSH channel
        :type channel: :py:class:`ssh2.channel.Channel`
        :param timeout: (Optional) Timeout setting
        :type timeout: int
        :param encoding: (Optional) Encoding to use for output. Must be valid
          `Python codec <https://docs.python.org/library/codecs.html>`_
        :type encoding: str

        :rtype: tuple(stdout, stderr)
        """
        channel = host_out.channel if channel is None else channel
        client = self.host_clients[host_out.host] if client is None else client
        stdout = client.read_output_buffer(
            client.read_output(channel, timeout=timeout), encoding=encoding)
        stderr = client.read_output_buffer(
            client.read_stderr(channel, timeout=timeout),
            prefix='\t[err]', encoding=encoding)
        host_out.stdout = stdout
        host_out.stderr = stderr
        return stdout, stderr