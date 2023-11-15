  def _SetSocketHighWaterMark(self):
    """Sets the high water mark for the socket.

    This number is the maximum number of items that will be queued in the socket
    on this end of the queue.
    """
    self._zmq_socket.hwm = self._high_water_mark