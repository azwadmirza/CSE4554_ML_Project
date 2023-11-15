  def _ZeroMQResponder(self, source_queue):
    """Listens for requests and replies to clients.

    Args:
      source_queue (Queue.queue):  queue to use to pull items from.

    Raises:
      QueueEmpty: If the queue encountered a timeout trying to push an item.
    """
    logging.debug(u'{0:s} responder thread started'.format(self.name))
    while not self._terminate_event.isSet():
      try:
        if self._closed_event.isSet():
          # No further items can be added be added to the queue, so we don't
          # need to block.
          item = source_queue.get_nowait()
        else:
          item = source_queue.get(True, timeout=self._buffer_timeout_seconds)

      except Queue.Empty:
        logging.debug(u'{0:s} queue was empty'.format(self.name))
        # Signal to any downstream queues that they should abort.
        item = plaso_queue.QueueAbort()
        # Exit after an attempt to inform downstream queues that there are no
        # more events.
        self._terminate_event.set()

      sent_successfully = self._SendItem(self._zmq_socket, item)
      if not sent_successfully:
        logging.error(u'Queue {0:s} error sending item.')
        break

    logging.info(u'Queue {0:s} responder exiting.'.format(self.name))
    self._zmq_socket.close(self._linger_seconds)