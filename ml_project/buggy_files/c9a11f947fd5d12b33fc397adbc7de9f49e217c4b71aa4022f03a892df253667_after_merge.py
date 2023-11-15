  def __init__(
      self, buffer_timeout_seconds=2, buffer_max_size=10000, delay_open=True,
      linger_seconds=10, maximum_items=1000, name=u'Unnamed', port=None,
      timeout_seconds=5):
    """Initializes a buffered, ZeroMQ backed queue.

    Args:
      buffer_max_size (Optional[int]): maximum number of items to store in
          the buffer, before or after they are sent/received via ZeroMQ.
      buffer_timeout_seconds(Optional[int]): number of seconds to wait when
          doing a put or get to/from the internal buffer.
      delay_open (Optional[bool]): whether a ZeroMQ socket should be created
          the first time the queue is pushed to or popped from, rather than at
          queue object initialization. This is useful if a queue needs to be
          passed to a child process from a parent process.
      linger_seconds (Optional[int]): number of seconds that the underlying
          ZeroMQ socket can remain open after the queue object has been closed,
          to allow queued items to be transferred to other ZeroMQ sockets.
      maximum_items (Optional[int]): maximum number of items to queue on the
          ZeroMQ socket. ZeroMQ refers to this value as "high water mark" or
          "hwm". Note that this limit only applies at one "end" of the queue.
          The default of 1000 is the ZeroMQ default value.
      name (Optional[str]): name to identify the queue.
      port (Optional[int]): The TCP port to use for the queue. None indicates
          that the queue should choose a random port to bind to.
      timeout_seconds (Optional[int]): number of seconds that calls to PopItem
          and PushItem may block for, before returning queue.QueueEmpty.
    """
    self._buffer_timeout_seconds = buffer_timeout_seconds
    self._queue = Queue.Queue(maxsize=buffer_max_size)
    self._zmq_thread = None
    # We need to set up the internal buffer queue before we call super, so that
    # if the call to super opens the ZMQSocket, the backing thread will work.
    super(ZeroMQBufferedQueue, self).__init__(
        delay_open=delay_open, linger_seconds=linger_seconds,
        maximum_items=maximum_items, name=name, port=port,
        timeout_seconds=timeout_seconds)