  def _ZeroMQResponder(self, source_queue, socket, terminate_event):
    """Listens for requests and replies to clients.

    Args:
      source_queue: The queue to uses to pull items from.
      socket: The socket to listen to, and send responses to.
      terminate_event: The event that signals that the queue should terminate.
    """