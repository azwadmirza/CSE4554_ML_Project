  def launch(self):
    """Launches pantsd in a subprocess.

    N.B. This should always be called under care of the `lifecycle_lock`.

    :returns: A Handle for the pantsd instance.
    :rtype: PantsDaemon.Handle
    """
    self.terminate(include_watchman=False)
    self.watchman_launcher.maybe_launch()
    self._logger.debug('launching pantsd')
    self.daemon_spawn()
    # Wait up to 60 seconds for pantsd to write its pidfile.
    pantsd_pid = self.await_pid(60)
    listening_port = self.read_named_socket('pailgun', int)
    self._logger.debug('pantsd is running at pid {}, pailgun port is {}'
                       .format(self.pid, listening_port))
    return self.Handle(pantsd_pid, listening_port)