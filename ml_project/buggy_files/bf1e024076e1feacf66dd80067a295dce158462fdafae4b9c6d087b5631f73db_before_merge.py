  def Close(self, abort=False):
    """Close the queue.

    Unless the abort parameter is set to true, the underlying socket will remain
    open for _linger_seconds before being destroyed.

    Args:
      abort: Whether the queue is closing due to an error condition, and the
             queue should be close immediately.
    """
    if abort:
      logging.warning(u'{0:s} Queue aborting. Contents may be lost.'.format(
          self.name))
      self.Empty()
      self._linger_seconds = 0
    else:
      logging.debug(
          u'{0:s} Queue closing, will linger for up to {1:d} seconds'.format(
              self.name, self._linger_seconds))

    if hasattr(self, u'terminate_event'):
      self._terminate_event.set()
    self._closed = True