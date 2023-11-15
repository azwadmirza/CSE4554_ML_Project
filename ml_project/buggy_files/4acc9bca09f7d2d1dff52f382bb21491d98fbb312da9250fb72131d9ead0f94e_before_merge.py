  def WriteInitialize(self):
    """Initializes the write of a serialized data stream.

    Creates a temporary file to store the serialized data.

    Returns:
      An integer containing the offset of the temporary file.

    Raises:
      IOError: if the serialized data stream cannot be written.
    """
    self._file_object = open(self._stream_name, 'wb')
    return self._file_object.tell()