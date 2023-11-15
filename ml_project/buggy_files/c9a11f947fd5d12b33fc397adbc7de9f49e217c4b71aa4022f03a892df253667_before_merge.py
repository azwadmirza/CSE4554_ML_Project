  def __init__(
      self, delay_open=True, linger_seconds=10, port=None, timeout_seconds=5,
      name=u'Unnamed', maximum_items=1000, buffer_max_size=10000,
      buffer_timeout_seconds=2):
    """Initializes a buffered, ZeroMQ backed queue.

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
      maximum_items: Optional maximum number of items allowed in the queue
                       at one time. Note that this limit only applies at one
                       "end" of the queue. The default of 1000 is the ZeroMQ
                       default value.
      buffer_max_size: The maximum number of items to store in the buffer,
                       before or after they are sent/received via ZeroMQ.
      buffer_timeout_seconds: The number of seconds to wait when doing a
                              put or get to/from the internal buffer.
    """
    self._buffer_timeout_seconds = buffer_timeout_seconds
    self._queue = Queue.Queue(maxsize=buffer_max_size)
    self._terminate_event = threading.Event()
    # We need to set up the internal buffer queue before we call super, so that
    # if the call to super opens the ZMQSocket, the backing thread will work.
    super(ZeroMQBufferedQueue, self).__init__(
        delay_open, linger_seconds, port, timeout_seconds, name,
        maximum_items)