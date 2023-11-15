  def PopItem(self):
    """Pops an item off the queue.

    If no ZeroMQ socket has been created, one will be created the first
    time this method is called.

    Returns:
      object: item from the queue.

    Raises:
      QueueEmpty: If the queue is empty, and no item could be popped within the
          queue timeout.
      zmq.error.ZMQError: If a ZeroMQ error occurs.
    """
    logging.debug(
        u'Pop on {0:s} queue, port {1:d}'.format(self.name, self.port))
    if not self._zmq_socket:
      self._CreateZMQSocket()

    last_retry_timestamp = time.time() + self.timeout_seconds
    while not self._terminate_event.isSet() and not self._closed_event.isSet():
      try:
        return self._ReceiveItemOnActivity(self._zmq_socket)

      except errors.QueueEmpty:
        if time.time() > last_retry_timestamp:
          raise

      except KeyboardInterrupt:
        self.Close(abort=True)
        raise