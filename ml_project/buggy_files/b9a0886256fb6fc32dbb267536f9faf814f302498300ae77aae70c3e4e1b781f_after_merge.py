  def CreateEvent(self, timestamp, offset, attributes):
    """Creates an event.

       This function should be overwritten by text parsers that required
       the generation of specific event object type, the default event
       type is TextEvent.

    Args:
      timestamp: the timestamp time value. The timestamp contains the
                 number of microseconds since Jan 1, 1970 00:00:00 UTC.
      offset: the offset of the event.
      attributes: a dictionary that contains the event's attributes.

    Returns:
      An event object (instance of TextEvent).
    """
    return text_events.TextEvent(timestamp, offset, attributes)