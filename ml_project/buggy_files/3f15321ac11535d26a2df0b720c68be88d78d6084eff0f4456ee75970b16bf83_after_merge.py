  def PopItem(self):
    """Pops an item off the queue.

    Returns:
      object: item from the queue.

    Raises:
      QueueEmpty: If the queue is empty, and no item could be popped within the
                  queue timeout.
    """