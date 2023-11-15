  def _CreateZMQSocket(self):
    """Creates a ZeroMQ socket."""
    logging.debug(u'Creating socket for {0:s}'.format(self.name))

    if not self._zmq_context:
      self._zmq_context = zmq.Context()

    if self._zmq_socket:
      logging.debug(u'Closing old socket for {0:s}'.format(self.name))
      self._zmq_socket.close()
      self._zmq_socket = None
    self._zmq_socket = self._zmq_context.socket(self._SOCKET_TYPE)
    self._SetSocketTimeouts()
    self._SetSocketHighWaterMark()

    if self.port:
      address = u'{0:s}:{1:d}'.format(self._SOCKET_ADDRESS, self.port)
      if self.SOCKET_CONNECTION_TYPE == self.SOCKET_CONNECTION_CONNECT:
        self._zmq_socket.connect(address)
        logging.debug(u'{0:s} connected to {1:s}'.format(self.name, address))
      else:
        self._zmq_socket.bind(address)
        logging.debug(
            u'{0:s} bound to specified port {1:s}'.format(self.name, address))
    else:
      self.port = self._zmq_socket.bind_to_random_port(self._SOCKET_ADDRESS)
      logging.debug(
          u'{0:s} bound to random port {1:d}'.format(self.name, self.port))