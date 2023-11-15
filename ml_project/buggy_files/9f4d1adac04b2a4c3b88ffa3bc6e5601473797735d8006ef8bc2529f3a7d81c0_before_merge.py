  def PushItem(self, item, block=True):
    """Push an item on to the queue.

    If no ZeroMQ socket has been created, one will be created the first time
    this method is called.

    Args:
      item: The item to push on to the queue.
      block: Optional argument to indicate whether the push should be performed
             in blocking or non-block mode.

    Raises:
      KeyboardInterrupt: If the process is sent a KeyboardInterrupt while
                         pushing an item.
      zmq.error.Again: If it was not possible to push the item to the queue
                       within the timeout.
      zmq.error.ZMQError: If a ZeroMQ specific error occurs.
    """
    logging.debug(u'Push on {0:s} queue, port {1:d}'.format(
        self.name, self.port))
    if not self._zmq_socket:
      self._CreateZMQSocket()
    try:
      if block:
        self._zmq_socket.send_pyobj(item)
      else:
        self._zmq_socket.send_pyobj(item, zmq.DONTWAIT)
    except zmq.error.Again:
      logging.error(u'{0:s} unable to push item, raising.'.format(self.name))
      raise
    except zmq.error.ZMQError as exception:
      if exception.errno == errno.EINTR:
        logging.error(u'ZMQ syscall interrupted in {0:s}.'.format(self.name))
        return plaso_queue.QueueAbort()
      else:
        raise
    except KeyboardInterrupt:
      self.Close(abort=True)
      raise