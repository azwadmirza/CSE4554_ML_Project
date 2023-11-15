  def _ZeroMQResponder(self, source_queue, socket, terminate_event):
    """Listens for requests and replies to clients.

    Args:
      source_queue: The queue to uses to pull items from.
      socket: The socket to listen to, and send responses to.
      terminate_event: The event that signals that the queue should terminate.

    Raises:
      zmq.error.ZMQError: If an error is encountered by ZeroMQ.
    """
    logging.debug(u'ZeroMQ responder thread started')
    while not terminate_event.isSet():
      try:
        item = socket.recv_pyobj()
      except zmq.error.Again:
        # No item received within timeout.
        item = plaso_queue.QueueAbort()
      except zmq.error.ZMQError as exception:
        if exception.errno == errno.EINTR:
          logging.error(u'ZMQ syscall interrupted in {0:s}.'.format(self.name))
          break
        else:
          raise

      retries = 0
      while retries < self._DOWNSTREAM_QUEUE_MAX_TRIES:
        try:
          self._queue.put(item, timeout=self._buffer_timeout_seconds)
          break
        except Queue.Full:
          logging.debug(u'Queue {0:s} buffer limit hit.'.format(self.name))
          retries += 1
          if retries >= self._DOWNSTREAM_QUEUE_MAX_TRIES:
            logging.error(u'Queue {0:s} unserved for too long, aborting'.format(
                self.name))
            break
          else:
            time.sleep(self._DOWNSTREAM_QUEUE_SLEEP_TIME)
            continue
    logging.info(u'Queue {0:s} responder exiting.'.format(self.name))