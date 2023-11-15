    def run_command(self, command, sudo=False, user=None, stop_on_errors=True,
                    shell=None, use_shell=True, use_pty=True, host_args=None,
                    encoding='utf-8', **paramiko_kwargs):
        """Run command on all hosts in parallel, honoring self.pool_size,
        and return output buffers.

        This function will block until all commands have been received
        by remote servers and then return immediately.

        More explicitly, function will return after connection and
        authentication establishment and after commands have been received by
        successfully established SSH channels.

        Any connection and/or authentication exceptions will be raised here
        and need catching *unless* ``run_command`` is called with
        ``stop_on_errors=False`` in which case exceptions are added to host
        output instead.

        :param command: Command to run
        :type command: str
        :param sudo: (Optional) Run with sudo. Defaults to False
        :type sudo: bool
        :param user: (Optional) User to run command as. Requires sudo access
          for that user from the logged in user account.
        :type user: str
        :param stop_on_errors: (Optional) Raise exception on errors running
          command. Defaults to True. With stop_on_errors set to False,
          exceptions are instead added to output of `run_command`. See example
          usage below.
        :type stop_on_errors: bool
        :param shell: (Optional) Override shell to use to run command with.
          Defaults to login user's defined shell. Use the shell's command
          syntax, eg `shell='bash -c'` or `shell='zsh -c'`.
        :type shell: str
        :param use_shell: (Optional) Run command with or without shell. Defaults
          to True - use shell defined in user login to run command string
        :type use_shell: bool
        :param use_pty: (Optional) Enable/Disable use of pseudo terminal
          emulation. Disabling it will prohibit capturing standard input/output.
          This is required in majority of cases, exceptions being where a shell
          is not used and/or input/output is not required. In particular
          when running a command which deliberately closes input/output pipes,
          such as a daemon process, you may want to disable ``use_pty``.
          Defaults to ``True``
        :type use_pty: bool
        :param host_args: (Optional) Format command string with per-host
          arguments in ``host_args``. ``host_args`` length must equal length of
          host list - :py:class:`pssh.exceptions.HostArgumentException` is
          raised otherwise
        :type host_args: tuple or list
        :param encoding: Encoding to use for output. Must be valid
            `Python codec <https://docs.python.org/2.7/library/codecs.html>`_
        :type encoding: str
        :param paramiko_kwargs: (Optional) Extra keyword arguments to be
          passed on to :py:func:`paramiko.client.SSHClient.connect`
        :type paramiko_kwargs: dict

        :rtype: Dictionary with host as key and
          :py:class:`pssh.output.HostOutput` as value as per
          :py:func:`pssh.pssh_client.ParallelSSHClient.get_output`

        :raises: :py:class:`pssh.exceptions.AuthenticationException` on
          authentication error
        :raises: :py:class:`pssh.exceptions.UnknownHostException` on DNS
          resolution error
        :raises: :py:class:`pssh.exceptions.ConnectionErrorException` on error
          connecting
        :raises: :py:class:`pssh.exceptions.SSHException` on other undefined SSH
          errors
        :raises: :py:class:`pssh.exceptions.HostArgumentException` on number of
          host arguments not equal to number of hosts
        :raises: :py:class:`TypeError` on not enough host arguments for cmd
          string format
        :raises: :py:class:`KeyError` on no host argument key in arguments
          dict for cmd string format"""
        output = {}
        if host_args:
            try:
                cmds = [self.pool.spawn(self._run_command, host,
                                        command % host_args[host_i],
                                        sudo=sudo, user=user, shell=shell,
                                        use_shell=use_shell, use_pty=use_pty,
                                        **paramiko_kwargs)
                        for host_i, host in enumerate(self.hosts)]
            except IndexError:
                raise HostArgumentException(
                    "Number of host arguments provided does not match "
                    "number of hosts ")
        else:
            cmds = [self.pool.spawn(
                self._run_command, host, command,
                sudo=sudo, user=user, shell=shell,
                use_shell=use_shell, use_pty=use_pty,
                **paramiko_kwargs)
                for host in self.hosts]
        for cmd in cmds:
            try:
                self.get_output(cmd, output, encoding=encoding)
            except Exception:
                if stop_on_errors:
                    raise
        return output