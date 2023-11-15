  def __init__(
      self, delay_open=True, linger_seconds=10, port=None, timeout_seconds=5,
      name=u'Unnamed', maximum_items=1000):
    """Initializes a ZeroMQ backed queue.

    Args:
      delay_open: Optional boolean that governs whether a ZeroMQ socket
                   should be created the first time the queue is pushed to or
                   popped from, rather than at queue object initialization.
                   This is useful if a queue needs to be passed to a
                   child process from a parent.
      linger_seconds: Optional number of seconds that the underlying ZeroMQ
                      socket can remain open after the queue object has been
                      closed, to allow queued items to be transferred to other
                      ZeroMQ sockets.
      port: The TCP port to use for the queue. The default is None, which
            indicates that the queue should choose a random port to bind to.
      timeout_seconds: Optional number of seconds that calls to PopItem and
                       PushItem may block for, before returning
                       queue.QueueEmpty.
      name: Optional name to identify the queue.
      maximum_items: Optional maximum number of items to queue on the ZeroMQ
                     socket. ZeroMQ refers to this value as "high water
                     mark" or "hwm". Note that this limit only applies at one
                     "end" of the queue. The default of 1000 is the ZeroMQ
                     default value.

    Raises:
      ValueError: If the queue is configured to connect to an endpoint,
                      but no port is specified.
    """
    if (self.SOCKET_CONNECTION_TYPE == self.SOCKET_CONNECTION_CONNECT
        and not port):
      raise ValueError(u'No port specified to connect to.')
    self._closed = False
    self._high_water_mark = maximum_items
    self._linger_seconds = linger_seconds
    self._timeout_milliseconds = timeout_seconds * 1000
    self._zmq_socket = None
    self.name = name
    self.port = port
    if not delay_open:
      self._CreateZMQSocket()