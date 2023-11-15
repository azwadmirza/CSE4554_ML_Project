  def PushItem(self, item, block=True):
    """Pushes an item onto the queue.

    Args:
      item (object): item to add.
      block (bool): whether to block if the queue is full.

    Raises:
      QueueFull: when the next call to PushItem would exceed the limit of items
          in the queue.
    """