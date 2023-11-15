  def __init__(self, identifier, store_number=0, store_offset=0):
    """Initializes the tag index value.

    Args:
      identifier: the identifier string.
      store_number: optional store number.
      store_offset: optional offset relative to the start of the store.
    """
    super(_EventTagIndexValue, self).__init__()
    self.identifier = identifier
    self.store_number = store_number
    self.store_offset = store_offset