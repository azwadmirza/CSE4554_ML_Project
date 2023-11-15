  def _ZeroMQResponder(self, source_queue):
    """Listens for requests and replies to clients.

    Args:
      source_queue (Queue.queue): queue to use to pull items from.

    Raises:
      QueueFull: if it was not possible to put an item into the buffer queue.
    """
    logging.debug(u'{0:s} responder thread started'.format(self.name))
    while not self._terminate_event.isSet() and not self._closed_event.isSet():
      try:
        item = self._ReceiveItemOnActivity(self._zmq_socket)

      except errors.QueueEmpty:
        # Timeout receiving an item, we just retry until the terminate event
        # is set.
        continue

      retries = 0
      while retries < self._DOWNSTREAM_QUEUE_MAX_TRIES:
        try:
          self._queue.put(item, timeout=self._buffer_timeout_seconds)
          break
        except Queue.Full:
          logging.debug(u'Queue {0:s} buffer limit hit.'.format(self.name))
          retries += 1
          if retries >= self._DOWNSTREAM_QUEUE_MAX_TRIES:
            logging.error(
                u'{0:s} buffer queue full for too long, aborting'.format(
                    self.name))
            raise errors.QueueFull
          else:
            time.sleep(self._DOWNSTREAM_QUEUE_SLEEP_TIME)
            continue

    logging.info(u'Queue {0:s} responder exiting.'.format(self.name))
    self._zmq_socket.close(self._linger_seconds)