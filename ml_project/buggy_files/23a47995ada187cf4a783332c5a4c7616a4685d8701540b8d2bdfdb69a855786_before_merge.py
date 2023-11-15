  def _ZeroMQResponder(self, source_queue, socket, terminate_event):
    """Listens for requests and replies to clients.

    Args:
      source_queue: The queue to uses to pull items from.
      socket: The socket to listen to, and send responses to.
      terminate_event: The event that signals that the queue should terminate.

    Raises:
      QueueEmpty: If a timeout occurs when trying to reply to a request.
      zmq.error.ZMQError: If an error occurs in ZeroMQ.
    """
    logging.debug(u'ZeroMQ responder thread started')
    while not terminate_event.isSet():
      try:
        # We need to receive a request before we send.
        _ = socket.recv()
      except zmq.error.Again:
        logging.debug(u'{0:s} did not receive a request within the '
                      u'timeout of {1:d} seconds.'.format(
                          self.name, self.timeout_seconds))
        continue
      except zmq.error.ZMQError as exception:
        if exception.errno == errno.EINTR:
          logging.error(u'ZMQ syscall interrupted in {0:s}.'.format(self.name))
          break
        else:
          raise

      try:
        if self._closed:
          item = source_queue.get_nowait()
        else:
          item = source_queue.get(True, self._buffer_timeout_seconds)
      except Queue.Empty:
        item = plaso_queue.QueueAbort()

      try:
        self._zmq_socket.send_pyobj(item)
      except zmq.error.Again:
        logging.debug(
            u'{0:s} could not reply to a request within {1:d} seconds.'.format(
                self.name, self.timeout_seconds))
        raise errors.QueueEmpty
      except zmq.error.ZMQError as exception:
        if exception.errno == errno.EINTR:
          logging.error(u'ZMQ syscall interrupted in {0:s}.'.format(self.name))
          break
        else:
          raise
    socket.close(self._linger_seconds)