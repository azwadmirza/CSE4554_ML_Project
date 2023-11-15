  def _ZeroMQResponder(self, source_queue):
    """Listens for requests and replies to clients.

    Args:
      source_queue (Queue.queue): queue to to pull items from.
    """