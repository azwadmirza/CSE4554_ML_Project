  def PushItem(self, item, block=True):
    """Push an item on to the queue.

    If no ZeroMQ socket has been created, one will be created the first time
    this method is called.

    Args:
      item (object): item to push on the queue.
      block (Optional[bool]): whether the push should be performed in blocking
          or non-block mode.

    Raises:
      QueueAlreadyClosed: If there is an attempt to push to a queue that's
          already closed.
    """
    if self._closed_event.isSet():
      raise errors.QueueAlreadyClosed()

    if not self._zmq_socket:
      self._CreateZMQSocket()

    self._queue.put(item, block=block, timeout=self._buffer_timeout_seconds)