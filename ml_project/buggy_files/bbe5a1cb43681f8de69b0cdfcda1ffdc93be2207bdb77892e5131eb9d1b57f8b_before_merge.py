  def __init__(self, timestamp, offset, attributes):
    """Initializes a text event object.

    Args:
      timestamp: The timestamp time value. The timestamp contains the
                 number of microseconds since Jan 1, 1970 00:00:00 UTC.
      offset: The offset of the attributes.
      attributes: A dict that contains the events attributes.
    """
    super(TextEvent, self).__init__(
        timestamp, eventdata.EventTimestamp.WRITTEN_TIME)

    self.offset = offset

    for name, value in iter(attributes.items()):
      # TODO: Revisit this constraints and see if we can implement
      # it using a more sane solution.
      if isinstance(value, py2to3.STRING_TYPES) and not value:
        continue
      setattr(self, name, value)