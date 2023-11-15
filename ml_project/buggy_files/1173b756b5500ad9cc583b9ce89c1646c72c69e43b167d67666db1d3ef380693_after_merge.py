  def _CreateZMQSocket(self):
    """Creates a ZeroMQ socket as well as a regular queue and a thread."""
    super(ZeroMQBufferedQueue, self)._CreateZMQSocket()
    if not self._zmq_thread:
      thread_name = u'{0:s}_zmq_responder'.format(self.name)
      self._zmq_thread = threading.Thread(
          target=self._ZeroMQResponder, args=[self._queue], name=thread_name)
      self._zmq_thread.start()