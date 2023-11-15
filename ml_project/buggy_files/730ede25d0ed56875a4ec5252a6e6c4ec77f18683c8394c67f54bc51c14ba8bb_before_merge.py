  def Close(self, abort=False):
    """Closes the queue.

    Args:
      abort: If the Close is the result of an abort condition.

    Raises:
      QueueAlreadyClosed: If the queue is not started, or has already been
      closed.
    """
    if self._closed and not abort:
      raise errors.QueueAlreadyClosed()

    if abort:
      logging.warning(u'{0:s} queue aborting. Contents may be lost.'.format(
          self.name))
      self._linger_seconds = 0
    else:
      logging.debug(
          u'{0:s} queue closing, will linger for up to {1:d} seconds'.format(
              self.name, self._linger_seconds))

    if not self._zmq_socket:
      return
    self._zmq_socket.close(self._linger_seconds)