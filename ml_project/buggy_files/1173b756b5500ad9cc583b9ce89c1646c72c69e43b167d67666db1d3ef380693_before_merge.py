  def _CreateZMQSocket(self):
    """Creates a ZeroMQ socket as well as a regular queue and a thread."""
    super(ZeroMQBufferedQueue, self)._CreateZMQSocket()
    self._zmq_thread = threading.Thread(
        target=self._ZeroMQResponder, args=(
            self._queue, self._zmq_socket, self._terminate_event))
    self._zmq_thread.daemon = True
    self._zmq_thread.start()