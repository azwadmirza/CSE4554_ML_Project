  def GetTimestamp(self, entry_index):
    """Retrieves a specific serialized data timestamp.

    Args:
      entry_index: an integer containing the table entry index.

    Returns:
      An integer containing the serialized data timestamp.

    Raises:
      IndexError: if the table entry index is out of bounds.
    """
    return self._timestamps[entry_index]