  def __init__(
      self, delay_open=True, linger_seconds=10, maximum_items=1000,
      name=u'Unnamed', port=None, timeout_seconds=5):
    """Initializes a ZeroMQ backed queue.

    Args:
      delay_open (Optional[bool]): whether a ZeroMQ socket should be created
          the first time the queue is pushed to or popped from, rather than at
          queue object initialization. This is useful if a queue needs to be
          passed to a child process from a parent process.
      linger_seconds (Optional[int]): number of seconds that the underlying
          ZeroMQ socket can remain open after the queue has been closed,
          to allow queued items to be transferred to other ZeroMQ sockets.
      maximum_items (Optional[int]): maximum number of items to queue on the
          ZeroMQ socket. ZeroMQ refers to this value as "high water mark" or
          "hwm". Note that this limit only applies at one "end" of the queue.
          The default of 1000 is the ZeroMQ default value.
      name (Optional[str]): Optional name to identify the queue.
      port (Optional[int]): The TCP port to use for the queue. The default is
          None, which indicates that the queue should choose a random port to
          bind to.
      timeout_seconds (Optional[int]): number of seconds that calls to PopItem
          and PushItem may block for, before returning queue.QueueEmpty.

    Raises:
      ValueError: If the queue is configured to connect to an endpoint,
          but no port is specified.
    """
    if (self.SOCKET_CONNECTION_TYPE == self.SOCKET_CONNECTION_CONNECT
        and not port):
      raise ValueError(u'No port specified to connect to.')
    self._closed_event = threading.Event()
    self._high_water_mark = maximum_items
    self._linger_seconds = linger_seconds
    self._terminate_event = threading.Event()
    self._zmq_context = None
    self._zmq_socket = None
    self.name = name
    self.port = port
    self.timeout_seconds = timeout_seconds
    if not delay_open:
      self._CreateZMQSocket()