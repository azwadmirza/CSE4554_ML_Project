  def __init__(self, zip_file, stream_name):
    """Initializes a serialized data timestamp table object.

    Args:
      zip_file: the ZIP file object that contains the stream.
      stream_name: string containing the name of the stream.
    """
    super(_SerializedDataTimestampTable, self).__init__()
    self._timestamps = []
    self._stream_name = stream_name
    self._zip_file = zip_file