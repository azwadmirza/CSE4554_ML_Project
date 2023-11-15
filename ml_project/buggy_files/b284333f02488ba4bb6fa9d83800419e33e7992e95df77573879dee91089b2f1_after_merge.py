  def _SetSocketTimeouts(self):
    """Sets the timeouts for socket send and receive."""
    receive_timeout = min(
        self._ZMQ_SOCKET_RECEIVE_TIMEOUT_MILLISECONDS, divmod(
            self.timeout_seconds, 1000))
    send_timeout = min(
        self._ZMQ_SOCKET_SEND_TIMEOUT_MILLISECONDS, divmod(
            self.timeout_seconds, 1000))
    self._zmq_socket.setsockopt(zmq.RCVTIMEO, receive_timeout)
    self._zmq_socket.setsockopt(zmq.SNDTIMEO, send_timeout)