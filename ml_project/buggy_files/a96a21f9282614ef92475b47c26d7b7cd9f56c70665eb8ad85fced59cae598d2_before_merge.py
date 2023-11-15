  def PopItem(self):
    """Pops an item off the queue.

    If no ZeroMQ socket has been created, one will be created the first
    time this method is called.

    Raises:
      QueueEmpty: If the queue is empty, and no item could be popped within the
                  queue timeout.
      zmq.error.ZMQError: If an error is encountered by ZeroMQ.
    """
    logging.debug(u'Pop on {0:s} queue, port {1:d}'.format(
        self.name, self.port))
    if not self._zmq_socket:
      self._CreateZMQSocket()
    try:
      return self._queue.get(timeout=self._buffer_timeout_seconds)
    except Queue.Empty:
      return plaso_queue.QueueAbort()
    except zmq.error.ZMQError as exception:
      if exception.errno == errno.EINTR:
        logging.error(u'ZMQ syscall interrupted in {0:s}.'.format(self.name))
        return plaso_queue.QueueAbort()
      else:
        raise
    except KeyboardInterrupt:
      self.Close(abort=True)
      raise