  def PushItem(self, item):
    """Pushes an item onto the queue.

    Raises:
      QueueFull: when the next call to PushItem would exceed the limit of items
                 in the queue.
    """