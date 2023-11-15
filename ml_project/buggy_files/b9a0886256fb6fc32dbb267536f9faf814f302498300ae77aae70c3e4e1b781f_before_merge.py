  def CreateEvent(self, timestamp, offset, attributes):
    """Creates an event.

       This function should be overwritten by text parsers that required
       the generation of specific event object type, the default event
       type is TextEvent.

    Args:
      timestamp: The timestamp time value. The timestamp contains the
                 number of microseconds since Jan 1, 1970 00:00:00 UTC.
      offset: The offset of the event.
      attributes: A dictionary that contains the event's attributes.

    Returns:
      An event object (instance of TextEvent).
    """
    return text_events.TextEvent(timestamp, offset, attributes)