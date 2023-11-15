  def _ZeroMQResponder(self, source_queue):
    """Listens for requests and replies to clients.

    Args:
      source_queue (Queue.queue): queue to use to pull items from.
    """
    logging.debug(u'{0:s} responder thread started'.format(self.name))

    item = None
    while not self._terminate_event.isSet():
      try:
        if self ._closed_event.isSet():
          item = source_queue.get_nowait()
        else:
          item = source_queue.get(True, self._buffer_timeout_seconds)

      except Queue.Empty:
        if self._closed_event.isSet():
          break

        continue

      try:
        # We need to receive a request before we can reply with the item.
        self._ReceiveItemOnActivity(self._zmq_socket)

      except errors.QueueEmpty:
        logging.warn(u'{0:s} timeout waiting for a request.'.format(self.name))
        if self._closed_event.isSet() and self._queue.empty():
          break

        continue

      sent_successfully = self._SendItem(self._zmq_socket, item)
      if not sent_successfully:
        logging.error(u'Queue {0:s} unable to send item.'.format(self.name))
        break

    logging.info(u'Queue {0:s} responder exiting.'.format(self.name))
    self._zmq_socket.close(self._linger_seconds)