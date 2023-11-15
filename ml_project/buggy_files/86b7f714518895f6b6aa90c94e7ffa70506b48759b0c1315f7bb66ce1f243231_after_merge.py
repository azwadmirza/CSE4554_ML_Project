  def _trapped_signals(self, client):
    """A contextmanager that handles SIGINT (control-c) and SIGQUIT (control-\\) remotely."""
    signal_handler = PailgunClientSignalHandler(
      client,
      timeout=self._bootstrap_options.for_global_scope().pantsd_pailgun_quit_timeout)
    with ExceptionSink.trapped_signals(signal_handler):
      yield