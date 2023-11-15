  def IsEmpty(self):
    """Checks if the queue is empty.

    ZeroMQ queues don't have a concept of "empty" - there could always be
    messages on the queue that a producer or consumer is unaware of. Thus,
    the queue is never empty, so we return False. Note that it is possible that
    a queue is unable to pop an item from a queue within a timeout, which will
    cause PopItem to raise a QueueEmpty exception, but this is a different
    condition.

    Returns:
      bool: False, to indicate the the queue isn't empty.
    """
    return False