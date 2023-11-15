  def IsConnected(self):
    """Checks if the queue is connected to an port."""
    if (self.SOCKET_CONNECTION_TYPE == self.SOCKET_CONNECTION_CONNECT and
        self.port is not None):
      return True
    return False