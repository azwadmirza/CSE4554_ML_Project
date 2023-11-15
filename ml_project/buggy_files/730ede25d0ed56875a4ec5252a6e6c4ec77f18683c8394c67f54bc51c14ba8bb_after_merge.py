  def Close(self, abort=False):
    """Closes the queue.

    Args:
      abort (Optional[bool]): whether the Close is the result of an abort
          condition. If True, queue contents may be lost.

    Raises:
      QueueAlreadyClosed: If the queue is not started, or has already been
          closed.
    """
    if self._closed_event.isSet() and not abort:
      raise errors.QueueAlreadyClosed()

    self._closed_event.set()

    if abort:
      logging.warning(
          u'{0:s} queue aborting. Contents may be lost.'.format(self.name))
      self._linger_seconds = 0
      # We can't determine whether a there might be an operation being performed
      # on the socket in a separate method or thread, so we'll signal that any
      # such operation should cease.
      self._terminate_event.set()

    else:
      logging.debug(
          u'{0:s} queue closing, will linger for up to {1:d} seconds'.format(
              self.name, self._linger_seconds))