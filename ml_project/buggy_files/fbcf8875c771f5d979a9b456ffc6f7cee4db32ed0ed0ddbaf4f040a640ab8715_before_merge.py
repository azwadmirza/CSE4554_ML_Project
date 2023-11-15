  def PopItem(self):
    """Pops an item of the queue.

    Provided for compatibility with the API, but doesn't actually work.

    Raises:
      WrongQueueType: As Pop is not supported by this queue.
    """
    raise errors.WrongQueueType()