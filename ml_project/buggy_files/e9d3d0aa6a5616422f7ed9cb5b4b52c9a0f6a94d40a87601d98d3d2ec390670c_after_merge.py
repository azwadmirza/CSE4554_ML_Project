  def __init__(self, zip_file, stream_name):
    """Initializes a serialized data stream object.

    Args:
      zip_file: the ZIP file object that contains the stream.
      stream_name: string containing the name of the stream.
    """
    super(_SerializedDataStream, self).__init__()
    self._entry_index = 0
    self._file_object = None
    self._stream_name = stream_name
    self._stream_offset = 0
    self._zip_file = zip_file