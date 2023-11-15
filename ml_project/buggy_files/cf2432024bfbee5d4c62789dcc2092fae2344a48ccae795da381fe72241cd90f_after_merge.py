  def __init__(
      self, tag_type, offset, event_uuid=None, store_number=None,
      store_offset=None):
    """Initializes the tag index value.

    Args:
      tag_type: an integer containing the tag type.
      offset: an integer containing the serialized event tag data offset.
      event_uuid: optional string containing the event identifier (UUID).
      store_number: optional integer containing the store number.
      store_offset: optional integer containing the offset relative
                    to the start of the store.
    """
    super(_EventTagIndexValue, self).__init__()
    self._identifier = None
    self.event_uuid = event_uuid
    self.offset = offset
    self.store_number = store_number
    self.store_offset = store_offset
    self.tag_type = tag_type