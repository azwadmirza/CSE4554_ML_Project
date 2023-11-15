  def PushItem(self, item, block=True):
    """Pushes an item on to the queue.

    Args:
      item (object): item to push on the queue.
      block (Optional[bool]): whether the push should be performed in blocking
          or non-block mode.

    Raises:
      QueueAlreadyClosed: If the queue is closed.
    """