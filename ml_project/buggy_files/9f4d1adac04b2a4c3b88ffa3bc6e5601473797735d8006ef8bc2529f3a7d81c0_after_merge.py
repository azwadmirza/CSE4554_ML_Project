  def PushItem(self, item, block=True):
    """Push an item on to the queue.

    If no ZeroMQ socket has been created, one will be created the first time
    this method is called.

    Args:
      item (object): item to push on the queue.
      block (Optional[bool]): whether the push should be performed in blocking
          or non-block mode.

    Raises:
      KeyboardInterrupt: If the process is sent a KeyboardInterrupt while
          pushing an item.
      errors.QueueFull: If it was not possible to push the item to the queue
          within the timeout.
      zmq.error.ZMQError: If a ZeroMQ specific error occurs.
    """
    logging.debug(
        u'Push on {0:s} queue, port {1:d}'.format(self.name, self.port))
    if not self._zmq_socket:
      self._CreateZMQSocket()

    last_retry_timestamp = time.time() + self.timeout_seconds
    while not self._terminate_event.isSet():
      try:
        send_successful = self._SendItem(self._zmq_socket, item, block)
        if send_successful:
          break

        if time.time() > last_retry_timestamp:
          logging.error(u'{0:s} unable to push item, raising.'.format(
              self.name))
          raise errors.QueueFull


      except KeyboardInterrupt:
        self.Close(abort=True)
        raise