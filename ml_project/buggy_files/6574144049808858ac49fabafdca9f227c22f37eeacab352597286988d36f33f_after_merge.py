  def PopItem(self):
    """Pops an item off the queue.

    If no ZeroMQ socket has been created, one will be created the first
    time this method is called.

    Returns:
      object: item from the queue.

    Raises:
      KeyboardInterrupt: If the process is sent a KeyboardInterrupt while
          popping an item.
      QueueEmpty: If the queue is empty, and no item could be popped within the
          queue timeout.
      zmq.error.ZMQError: If an error occurs in ZeroMQ.
    """
    logging.debug(
        u'Pop on {0:s} queue, port {1:d}'.format(self.name, self.port))

    if not self._zmq_socket:
      self._CreateZMQSocket()

    last_retry_time = time.time() + self.timeout_seconds
    while not self._terminate_event.isSet():
      try:
        self._zmq_socket.send_pyobj(None)
        break

      except zmq.error.Again:
        # The existing socket is now out of sync, so we need to open a new one.
        self._CreateZMQSocket()
        if time.time() > last_retry_time:
          logging.warn(u'{0:s} timeout requesting item'.format(self.name))
          raise errors.QueueEmpty

        continue

    while not self._terminate_event.isSet():
      try:
        return self._ReceiveItemOnActivity(self._zmq_socket)
      except errors.QueueEmpty:
        continue

      except KeyboardInterrupt:
        self.Close(abort=True)
        raise