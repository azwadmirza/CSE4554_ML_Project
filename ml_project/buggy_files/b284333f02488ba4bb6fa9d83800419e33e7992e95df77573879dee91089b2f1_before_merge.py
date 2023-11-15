  def _SetSocketTimeouts(self):
    """Sets the timeouts for socket send and receive."""
    if self._SOCKET_TYPE == zmq.PULL:
      self._zmq_socket.setsockopt(
          zmq.RCVTIMEO, self._timeout_milliseconds)
    elif self._SOCKET_TYPE == zmq.PUSH:
      self._zmq_socket.setsockopt(
          zmq.SNDTIMEO, self._timeout_milliseconds)