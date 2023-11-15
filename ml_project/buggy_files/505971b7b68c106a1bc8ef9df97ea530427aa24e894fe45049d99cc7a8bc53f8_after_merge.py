    def scp_send(self, local_file, remote_file, recurse=False):
        """Copy local file to remote file in parallel via SCP.

        This function returns a list of greenlets which can be
        `join`-ed on to wait for completion.

        :py:func:`gevent.joinall` function may be used to join on all greenlets
        and will also raise exceptions from them if called with
        ``raise_error=True`` - default is `False`.

        Alternatively call `.get()` on each greenlet to raise any exceptions
        from it.

        .. note::
          Creating remote directories when either ``remote_file`` contains
          directory paths or ``recurse`` is enabled requires SFTP support on
          the server as libssh2 SCP implementation lacks directory creation
          support.

        :param local_file: Local filepath to copy to remote host
        :type local_file: str
        :param remote_file: Remote filepath on remote host to copy file to
        :type remote_file: str
        :param recurse: Whether or not to descend into directories recursively.
        :type recurse: bool

        :rtype: list(:py:class:`gevent.Greenlet`) of greenlets for remote copy
          commands.

        :raises: :py:class:`pss.exceptions.SCPError` on errors copying file.
        :raises: :py:class:`OSError` on local OS errors like permission denied.
        """
        return [self.pool.spawn(self._scp_send, host_i, host, local_file,
                                remote_file, recurse=recurse)
                for host_i, host in enumerate(self.hosts)]