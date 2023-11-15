  def SignalAbort(self):
    """Signals the process to abort."""
    self._abort = True
    self._foreman_status_wait_event.set()