  def _ZeroMQResponder(self, source_queue, socket, terminate_event):
    """Listens for requests and replies to clients.

    Args:
      source_queue: The queue to uses to pull items from.
      socket: The socket to listen to, and send responses to.
      terminate_event: The event that signals that the queue should terminate.

    Raises:
      QueueEmpty: If the queue encountered a timeout trying to push an item.
      zmq.error.ZMQError: If ZeroMQ encounters an error.
    """
    logging.debug(u'ZeroMQ responder thread started')
    while not terminate_event.isSet():
      try:
        if self._closed:
          # No further items can be added be added to the queue, so we don't
          # need to block.
          item = source_queue.get_nowait()
        else:
          item = source_queue.get(True, timeout=self._buffer_timeout_seconds)
      except Queue.Empty:
        # No item available within timeout, so time to exit.
        self.Close()
        continue

      try:
        self._zmq_socket.send_pyobj(item)
      except zmq.error.Again:
        logging.debug(
            u'{0:s} could not push an item within {1:d} seconds.'.format(
                self.name, self.timeout_seconds))
        raise errors.QueueEmpty
      except zmq.error.ZMQError as exception:
        if exception.errno == errno.EINTR:
          logging.error(u'ZMQ syscall interrupted in {0:s}.'.format(self.name))
          break
        else:
          raise
    socket.close(self._linger_seconds)