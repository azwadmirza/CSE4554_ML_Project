    def scp_recv(self, remote_file, local_file, recurse=False, copy_args=None,
                 suffix_separator='_'):
        """Copy remote file(s) in parallel via SCP as
        <local_file><suffix_separator><host> or as per ``copy_args`` argument.

        With a ``local_file`` value of ``myfile`` and default separator ``_``
        the resulting filename will be ``myfile_myhost`` for the file from host
        ``myhost``.

        De-duplication behaviour is configurable by providing ``copy_args``
        argument, see below.

        This function, like :py:func:`ParallelSSHClient.scp_send`, returns a
        list of greenlets which can be `join`-ed on to wait for completion.

        :py:func:`gevent.joinall` function may be used to join on all greenlets
        and will also raise exceptions if called with ``raise_error=True`` -
        default is `False`.

        Alternatively call `.get` on each greenlet to raise any exceptions from
        it.

        Exceptions listed here are raised when
        either ``gevent.joinall(<greenlets>, raise_error=True)`` is called
        or ``.get`` is called on each greenlet, not this function itself.

        :param remote_file: remote filepath to copy to local host
        :type remote_file: str
        :param local_file: local filepath on local host to copy file to
        :type local_file: str
        :param recurse: whether or not to recurse
        :type recurse: bool
        :param suffix_separator: (Optional) Separator string between
          filename and host, defaults to ``_``. For example, for a
          ``local_file`` value of ``myfile`` and default separator the
          resulting filename will be ``myfile_myhost`` for the file from
          host ``myhost``. ``suffix_separator`` has no meaning if
          ``copy_args`` is provided
        :type suffix_separator: str
        :param copy_args: (Optional) format remote_file and local_file strings
          with per-host arguments in ``copy_args``. ``copy_args`` length *must*
          equal length of host list -
          :py:class:`pssh.exceptions.HostArgumentException` is raised otherwise
        :type copy_args: tuple or list

        :rtype: list(:py:class:`gevent.Greenlet`) of greenlets for remote copy
          commands.

        :raises: :py:class:`ValueError` when a directory is supplied to
          local_file and recurse is not set.
        :raises: :py:class:`pssh.exceptions.HostArgumentException` on number of
          per-host copy arguments not equal to number of hosts.
        :raises: :py:class:`pss.exceptions.SCPError` on errors copying file.
        :raises: :py:class:`OSError` on local OS errors like permission denied.

        .. note ::
          Local directories in ``local_file`` that do not exist will be
          created as long as permissions allow.

        .. note ::
          File names will be de-duplicated by appending the hostname to the
          filepath separated by ``suffix_separator`` or as per ``copy_args``
          argument if provided.
        """
        copy_args = [{'local_file': suffix_separator.join([local_file, host]),
                      'remote_file': remote_file}
                     for i, host in enumerate(self.hosts)] \
            if copy_args is None else copy_args
        local_file = "%(local_file)s"
        remote_file = "%(remote_file)s"
        try:
            return [self.pool.spawn(
                self._scp_recv, host,
                remote_file % copy_args[host_i],
                local_file % copy_args[host_i], recurse=recurse)
                    for host_i, host in enumerate(self.hosts)]
        except IndexError:
            raise HostArgumentException(
                "Number of per-host copy arguments provided does not match "
                "number of hosts")