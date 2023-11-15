  def WriteEntry(self, data):
    """Writes an entry to the file-like object.

    Args:
      data (bytes): data.

    Returns:
      int: offset of the entry within the temporary file.

    Raises:
      IOError: if the serialized data stream was not opened for writing or
          the entry cannot be written to the serialized data stream.
    """
    if not self._file_object:
      raise IOError(u'Unable to write to closed serialized data stream.')

    data_size = len(data)
    data_end_offset = (
        self._file_object.tell() + self._DATA_ENTRY_SIZE + data_size)
    if data_end_offset > self._maximum_data_size:
      raise IOError(u'Unable to write data entry size value out of bounds.')

    data_size = construct.ULInt32(u'size').build(data_size)
    self._file_object.write(data_size)
    self._file_object.write(data)

    return self._file_object.tell()